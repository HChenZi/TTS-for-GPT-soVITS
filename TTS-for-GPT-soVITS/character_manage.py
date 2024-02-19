global character_name

import os, json

from inference_core import get_tts_wav, change_sovits_weights, change_gpt_weights

def load_infer_config(config_path='infer_config.json'):
    """加载环境配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

import os
import json

def auto_get_infer_config(character_path):
    ## TODO: Auto-generate wav-list and prompt-list from character_path
    ##     
    # Initialize variables for file detection
    ckpt_file_found = None
    pth_file_found = None
    wav_file_found = None

    # Iterate through files in character_path to find matching file types
    for dirpath, dirnames, filenames in os.walk(character_path):
        for file in filenames:
            # 构建文件的完整路径
            full_path = os.path.join(dirpath, file)
            
            # 根据文件扩展名和变量是否已赋值来更新变量
            if file.endswith(".ckpt") and ckpt_file_found is None:
                ckpt_file_found = full_path
            elif file.endswith(".pth") and pth_file_found is None:
                pth_file_found = full_path
            elif file.endswith(".wav") and wav_file_found is None:
                wav_file_found = full_path

    # Initialize infer_config with gpt_path and sovits_path regardless of wav_file_found
    infer_config = {
        "gpt_path": ckpt_file_found,
        "sovits_path": pth_file_found
    }

    # If wav file is also found, update infer_config to include ref_wav_path, prompt_text, and prompt_language
    if wav_file_found:
        wav_file_name = os.path.splitext(os.path.basename(wav_file_found))[0]  # Extract the filename without extension
        infer_config.update({
            "ref_wav_path": wav_file_found,
            "prompt_text": wav_file_name,  # Use the extracted wav file name
            "prompt_language": "中文",
        })
    else:
        raise Exception("找不到wav参考文件！请把有效wav文件放置在trained文件夹下。否则效果可能会非常怪")
        pass
    # Check if the essential model files were found
    if ckpt_file_found and pth_file_found:
        infer_config_path = os.path.join(character_path, "infer_config.json")
        try:
            with open(infer_config_path , 'w', encoding='utf-8') as f:
                json.dump(infer_config, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"无法写入文件: {infer_config_path}. 错误: {e}")

        return infer_config_path
    else:
        return "Required model files (.ckpt or .pth) not found in character_path directory."


def load_character(character_name):
    try:
        # 加载配置
        config = load_infer_config(f"trained/{character_name}/infer_config.json")
        # 尝试从环境变量获取gpt_path，如果未设置，则从配置文件读取
        gpt_path = config.get("gpt_path")
        # 尝试从环境变量获取sovits_path，如果未设置，则从配置文件读取
        sovits_path = config.get("sovits_path")
    except:
        try:
            # 尝试调用auto_get_infer_config
            auto_get_infer_config(f"trained/{character_name}/")
            load_character(character_name)
            return 
        except:
            # 报错
            raise Exception("找不到模型文件！请把有效模型放置在trained文件夹下。")
    # 修改权重
    change_sovits_weights(sovits_path)
    change_gpt_weights(gpt_path)

def get_deflaut_character_name():
    import os
    import json

    character_info_path = "trained/character_info.json"
    default_character = None

    if os.path.exists(character_info_path):
        with open(character_info_path, "r", encoding='utf-8') as f:
            character_info = json.load(f)
            default_character = character_info.get("deflaut_character")

    if default_character is None:
        # List all items in "trained"
        all_items = os.listdir("trained")
        
        # Filter out only directories (folders) from all_items
        trained_folders = [item for item in all_items if os.path.isdir(os.path.join("trained", item))]
        
        # If there are any directories found, set the first one as the default character
        if trained_folders:
            default_character = trained_folders[0]

    return default_character


character_name = get_deflaut_character_name()

load_character(character_name)


def get_wav_from_text_api(text, text_language, top_k=12, top_p=0.6, temperature=0.6):
    # 加载环境配置
    config = load_infer_config(f"trained/{character_name}/infer_config.json")
    
    # 尝试从配置中提取参数，如果找不到则设置为None
    ref_wav_path = config.get('ref_wav_path', None)
    prompt_text = config.get('prompt_text', None)
    prompt_language = config.get('prompt_language', '中文')

    
    # 根据是否找到ref_wav_path和prompt_text、prompt_language来决定ref_free的值
    if ref_wav_path is not None and prompt_text is not None and prompt_language is not None:
        ref_free = False
    else:
        ref_free = True
        top_k = 3
        top_p = 0.3
        temperature = 0.3
       

    # 调用原始的get_tts_wav函数
    # 注意：这里假设get_tts_wav函数及其所需的其它依赖已经定义并可用
    return get_tts_wav(ref_wav_path, prompt_text, prompt_language, text, text_language, top_k=top_k, top_p=top_p, temperature=temperature, ref_free=ref_free)


def test_audio_save():
    fs, audio_to_save=get_wav_from_text_api("""这是一段音频测试""",'多语种混合')
    file_path = "testaudio/example_audio.wav"
    from scipy.io.wavfile import write
    write(file_path, fs, audio_to_save)


# test_audio_save()
