#!/bin/bash
# generate-audio.sh - 调用 edge-tts 或 sag CLI 生成高质量中文TTS音频
#
# 功能：
# - 默认使用 edge-tts，sag 作为备选
# - 支持双引擎切换和声音选择
# - 错误处理和重试机制
# - 音频质量检查和验证
# - 支持批量处理
#
# 使用方法：
# bash generate-audio.sh input_script.txt output_audio.mp3
# bash generate-audio.sh input_script.txt output_audio.mp3 --engine edge-tts
# bash generate-audio.sh input_script.txt output_audio.mp3 --engine sag
# bash generate-audio.sh input_script.txt output_audio.mp3 --voice zh-CN-XiaoxiaoNeural
#
# 依赖：
# - edge-tts (pip install edge-tts) - 默认引擎
# - sag CLI (ElevenLabs TTS) - 备选引擎
# - ffmpeg (可选，用于音频格式转换和质量检查)
#
# 作者：太森的AI助手二丫
# 版本：v3.0 - edge-tts优先版本

set -e  # 出错时退出

# 默认配置
DEFAULT_TTS_ENGINE="edge-tts"
DEFAULT_VOICE="zh-CN-YunxiNeural"  # 云希，太森喜欢的声音
DEFAULT_RATE="+15%"  # 提速15%
DEFAULT_SAG_MODEL="eleven_multilingual_v2"
DEFAULT_LANG="zh"
MAX_RETRIES=3
MIN_AUDIO_SIZE=20480   # 20KB，edge-tts短文本生成的文件大小
MAX_AUDIO_SIZE=104857600  # 100MB，最大音频文件大小

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
generate-audio.sh - 论文播客TTS音频生成工具 (edge-tts优先版)

使用方法:
    bash generate-audio.sh <input_script.txt> <output_audio.mp3> [options]

参数:
    input_script.txt    输入的播客脚本文件
    output_audio.mp3    输出的音频文件

选项:
    --engine ENGINE     TTS引擎选择 (edge-tts|sag, 默认: edge-tts)
    --voice VOICE       语音选择 (默认: zh-CN-YunyangNeural)
    --model-id MODEL    sag引擎的模型ID (默认: eleven_multilingual_v2)
    --lang LANG         语言代码 (默认: zh)
    --retry NUM         重试次数 (默认: 3)
    --help, -h          显示帮助信息

示例:
    bash generate-audio.sh podcast_script.txt podcast_audio.mp3
    bash generate-audio.sh script.txt audio.mp3 --engine edge-tts
    bash generate-audio.sh script.txt audio.mp3 --engine sag --model-id eleven_multilingual_v2
    bash generate-audio.sh script.txt audio.mp3 --voice zh-CN-XiaoxiaoNeural

支持的edge-tts中文声音:
    - zh-CN-YunyangNeural  (Male, News, Professional) ← 默认推荐
    - zh-CN-XiaoxiaoNeural (Female, Warm)
    - zh-CN-YunjianNeural  (Male, Passion)
    - zh-CN-YunxiNeural    (Male, Lively)

支持的sag TTS模型:
    - eleven_multilingual_v2 (默认，多语言高质量)
    - eleven_monolingual_v1 (单语言，速度较快)
    - eleven_multilingual_v1 (多语言，较旧版本)

注意：
    - edge-tts为默认引擎，免费且稳定
    - sag需要已安装并配置好ElevenLabs API key
    - 脚本文件应为UTF-8编码
    - 建议脚本长度3000-5000字，对应20-30分钟音频
EOF
}

# 检查依赖
check_dependencies() {
    local engine="$1"
    
    log_info "检查依赖..."
    
    if [[ "$engine" == "edge-tts" ]]; then
        # 检查edge-tts
        if ! python3 -m edge_tts --help &> /dev/null; then
            log_error "未找到 edge-tts，请先安装"
            log_error "安装方法：pip install edge-tts"
            return 1
        fi
        log_info "✓ edge-tts 可用"
        
    elif [[ "$engine" == "sag" ]]; then
        # 检查sag CLI
        if ! command -v sag &> /dev/null; then
            log_error "未找到 sag CLI，请先安装 ElevenLabs TTS CLI"
            log_error "安装方法：npm install -g @elevenlabs/sag"
            return 1
        fi
        
        # 检查sag配置
        if ! sag --help &> /dev/null; then
            log_error "sag CLI 未正确配置或无权限访问"
            log_error "请检查 ElevenLabs API key 配置"
            return 1
        fi
        log_info "✓ sag CLI 可用"
    fi
    
    # 检查ffmpeg (可选)
    if command -v ffmpeg &> /dev/null; then
        FFMPEG_AVAILABLE=true
        log_info "✓ ffmpeg 可用，将进行音频质量验证"
    else
        FFMPEG_AVAILABLE=false
        log_warn "未检测到 ffmpeg，跳过音频质量验证"
    fi
    
    log_success "依赖检查完成"
    return 0
}

# 验证输入文件
validate_input_file() {
    local input_file="$1"
    
    log_info "验证输入文件: $input_file"
    
    # 检查文件是否存在
    if [[ ! -f "$input_file" ]]; then
        log_error "输入文件不存在: $input_file"
        return 1
    fi
    
    # 检查文件大小
    local file_size=$(stat -f%z "$input_file" 2>/dev/null || stat -c%s "$input_file" 2>/dev/null || echo 0)
    if [[ $file_size -eq 0 ]]; then
        log_error "输入文件为空: $input_file"
        return 1
    fi
    
    if [[ $file_size -gt 1048576 ]]; then  # 1MB
        log_warn "输入文件较大 ($(($file_size / 1024))KB)，TTS生成可能需要较长时间"
    fi
    
    # 检查文件编码（简单检查）
    if file "$input_file" | grep -q "UTF-8"; then
        log_info "文件编码: UTF-8 ✓"
    else
        log_warn "文件可能不是UTF-8编码，可能影响中文TTS质量"
    fi
    
    # 统计字符数
    local char_count=$(wc -m < "$input_file")
    log_info "脚本字符数: $char_count"
    
    if [[ $char_count -lt 1000 ]]; then
        log_warn "脚本内容较少 ($char_count 字符)，生成的音频可能很短"
    elif [[ $char_count -gt 10000 ]]; then
        log_warn "脚本内容较多 ($char_count 字符)，TTS生成时间可能很长"
    fi
    
    # 预估音频时长（中文约160字/分钟）
    local estimated_minutes=$(($char_count / 160))
    if [[ $estimated_minutes -eq 0 ]]; then
        estimated_minutes=1
    fi
    log_info "预估音频时长: 约 $estimated_minutes 分钟"
    
    log_success "输入文件验证通过"
    return 0
}

# edge-tts音频生成函数
generate_edge_tts() {
    local input_file="$1"
    local output_file="$2"
    local voice="$3"
    
    log_info "使用 edge-tts 生成音频..."
    log_info "声音: $voice"
    
    # edge-tts命令
    local cmd="python3 -m edge_tts --voice \"$voice\" --rate=\"$DEFAULT_RATE\" --file \"$input_file\" --write-media \"$output_file\""
    log_info "执行命令: $cmd"
    
    if eval "$cmd"; then
        return 0
    else
        return 1
    fi
}

# sag音频生成函数
generate_sag_tts() {
    local input_file="$1"
    local output_file="$2"
    local model_id="$3"
    local lang="$4"
    
    log_info "使用 sag 生成音频..."
    log_info "模型: $model_id, 语言: $lang"
    
    # sag命令（输出到文件时自动禁用播放）
    local cmd="sag speak -f \"$input_file\" -o \"$output_file\" --lang $lang --model-id $model_id"
    log_info "执行命令: $cmd"
    
    if eval "$cmd"; then
        return 0
    else
        return 1
    fi
}

# 生成TTS音频主函数
generate_tts_audio() {
    local input_file="$1"
    local output_file="$2"
    local engine="$3"
    local voice="$4"
    local model_id="$5"
    local lang="$6"
    local retry_count="$7"
    
    log_info "开始生成TTS音频..."
    log_info "输入脚本: $input_file"
    log_info "输出音频: $output_file"
    log_info "TTS引擎: $engine"
    
    local attempt=1
    while [[ $attempt -le $retry_count ]]; do
        log_info "尝试生成音频 (第 $attempt 次)..."
        
        # 记录开始时间
        local start_time=$(date +%s)
        local tts_success=false
        
        # 根据引擎选择生成方法
        if [[ "$engine" == "edge-tts" ]]; then
            if generate_edge_tts "$input_file" "$output_file" "$voice"; then
                tts_success=true
            fi
        elif [[ "$engine" == "sag" ]]; then
            if generate_sag_tts "$input_file" "$output_file" "$model_id" "$lang"; then
                tts_success=true
            fi
        fi
        
        if [[ "$tts_success" == "true" ]]; then
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            
            log_success "TTS生成完成，耗时: ${duration}秒"
            
            # 验证输出文件
            if validate_output_audio "$output_file"; then
                return 0
            else
                log_warn "输出音频验证失败，准备重试..."
                rm -f "$output_file"  # 删除有问题的文件
            fi
        else
            log_error "TTS生成失败 (第 $attempt 次尝试)"
        fi
        
        attempt=$((attempt + 1))
        
        # 重试前等待
        if [[ $attempt -le $retry_count ]]; then
            log_info "等待 5 秒后重试..."
            sleep 5
        fi
    done
    
    log_error "TTS生成失败，已重试 $retry_count 次"
    return 1
}

# 验证输出音频文件
validate_output_audio() {
    local output_file="$1"
    
    log_info "验证输出音频: $output_file"
    
    # 检查文件是否存在
    if [[ ! -f "$output_file" ]]; then
        log_error "输出音频文件不存在"
        return 1
    fi
    
    # 检查文件大小
    local file_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null || echo 0)
    
    if [[ $file_size -lt $MIN_AUDIO_SIZE ]]; then
        log_error "音频文件过小 ($(($file_size / 1024))KB)，可能生成失败"
        return 1
    fi
    
    if [[ $file_size -gt $MAX_AUDIO_SIZE ]]; then
        log_warn "音频文件过大 ($(($file_size / 1024 / 1024))MB)，但继续处理"
    fi
    
    log_info "音频文件大小: $(($file_size / 1024 / 1024))MB"
    
    # 使用ffmpeg验证音频格式和质量
    if [[ "$FFMPEG_AVAILABLE" == "true" ]]; then
        log_info "使用 ffmpeg 验证音频质量..."
        
        # 获取音频信息
        local audio_info=$(ffmpeg -i "$output_file" 2>&1 | grep "Duration\|Audio:")
        
        if echo "$audio_info" | grep -q "Duration:"; then
            local duration=$(echo "$audio_info" | grep "Duration:" | sed 's/.*Duration: \([^,]*\).*/\1/')
            log_info "音频时长: $duration"
            
            # 检查时长是否合理（至少10秒，edge-tts短文本也可能很短）
            local duration_seconds=$(echo "$duration" | awk -F: '{print ($1 * 3600) + ($2 * 60) + $3}' | cut -d. -f1)
            if [[ $duration_seconds -lt 10 ]]; then
                log_warn "音频时长较短 ($duration)，但仍接受"
            fi
        fi
        
        if echo "$audio_info" | grep -q "Audio:"; then
            local audio_format=$(echo "$audio_info" | grep "Audio:" | head -1)
            log_info "音频格式: $audio_format"
        fi
        
        # 简单的音频完整性检查
        if ffmpeg -v error -i "$output_file" -f null - 2>&1 | grep -q "error"; then
            log_error "音频文件可能已损坏"
            return 1
        fi
        
        log_success "音频质量验证通过"
    fi
    
    log_success "输出音频验证通过"
    return 0
}

# 清理临时文件
cleanup() {
    # 如果有临时文件需要清理，在这里处理
    log_info "清理完成"
}

# 主函数
main() {
    local input_file=""
    local output_file=""
    local engine="$DEFAULT_TTS_ENGINE"
    local voice="$DEFAULT_VOICE"
    local model_id="$DEFAULT_SAG_MODEL"
    local lang="$DEFAULT_LANG"
    local retry_count="$MAX_RETRIES"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --engine)
                engine="$2"
                if [[ "$engine" != "edge-tts" && "$engine" != "sag" ]]; then
                    log_error "无效的引擎选择: $engine (支持: edge-tts, sag)"
                    exit 1
                fi
                shift 2
                ;;
            --voice)
                voice="$2"
                shift 2
                ;;
            --model-id)
                model_id="$2"
                shift 2
                ;;
            --lang)
                lang="$2"
                shift 2
                ;;
            --retry)
                retry_count="$2"
                shift 2
                ;;
            --no-play)
                # 兼容性参数，已默认不播放
                shift
                ;;
            -*)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
            *)
                if [[ -z "$input_file" ]]; then
                    input_file="$1"
                elif [[ -z "$output_file" ]]; then
                    output_file="$1"
                else
                    log_error "过多的位置参数: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # 检查必需参数
    if [[ -z "$input_file" ]] || [[ -z "$output_file" ]]; then
        log_error "缺少必需参数"
        show_help
        exit 1
    fi
    
    # 验证重试次数
    if ! [[ "$retry_count" =~ ^[0-9]+$ ]] || [[ $retry_count -lt 1 ]] || [[ $retry_count -gt 10 ]]; then
        log_error "无效的重试次数: $retry_count (应为1-10之间的整数)"
        exit 1
    fi
    
    log_info "=== 论文播客TTS音频生成开始 ==="
    log_info "时间: $(date)"
    log_info "引擎: $engine"
    
    # 设置清理函数
    trap cleanup EXIT
    
    # 执行主要步骤
    if ! check_dependencies "$engine"; then
        exit 1
    fi
    
    if ! validate_input_file "$input_file"; then
        exit 1
    fi
    
    if ! generate_tts_audio "$input_file" "$output_file" "$engine" "$voice" "$model_id" "$lang" "$retry_count"; then
        exit 1
    fi
    
    log_info "=== TTS音频生成完成 ==="
    log_success "✅ 输出文件: $output_file"
    
    # 显示最终统计信息
    if [[ -f "$output_file" ]]; then
        local final_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null || echo 0)
        log_info "📊 最终文件大小: $(($final_size / 1024 / 1024))MB"
        
        if [[ "$FFMPEG_AVAILABLE" == "true" ]]; then
            local duration=$(ffmpeg -i "$output_file" 2>&1 | grep "Duration:" | sed 's/.*Duration: \([^,]*\).*/\1/' | head -1)
            if [[ -n "$duration" ]]; then
                log_info "🎵 音频时长: $duration"
            fi
        fi
    fi
    
    log_success "🎉 播客音频生成成功！使用了 $engine 引擎"
}

# 脚本入口点
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi