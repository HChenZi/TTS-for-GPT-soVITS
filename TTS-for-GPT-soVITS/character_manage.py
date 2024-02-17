global character_name

import os, json

from inference_core import get_tts_wav, change_sovits_weights, change_gpt_weights

def load_infer_config(config_path='infer_config.json'):
    """加载环境配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def auto_get_infer_config(character_path):
    ## TODO: Auto-generate wav-list and prompt-list from character_path
    ##     
    # Initialize variables for file detection
    ckpt_file_found = None
    pth_file_found = None
    wav_file_found = None

    # Iterate through files in character_path to find matching file types
    for file in os.listdir(character_path):
        if file.endswith(".ckpt"):
            ckpt_file_found = os.path.join(character_path, file)
        elif file.endswith(".pth"):
            pth_file_found = os.path.join(character_path, file)
        elif file.endswith(".wav"):
            wav_file_found = os.path.join(character_path, file)

    # If all required files are found, create the infer_config
    if ckpt_file_found and pth_file_found and wav_file_found:
        wav_file_name = os.path.splitext(os.path.basename(wav_file_found))[0]  # Extract the filename without extension

        infer_config = {
            "ref_wav_path": wav_file_found,
            "prompt_text": wav_file_name,  # Use the extracted wav file name
            "prompt_language": "中文",
            "text_language": "中文",
            "gpt_path": ckpt_file_found,
            "sovits_path": pth_file_found
        }

        infer_config_path = os.path.join(character_path, "infer_config.json")
        with open(infer_config_path, "w") as f:
            json.dump(infer_config, f)

        return infer_config_path
    else:
        return "Required files not found in character_path directory."

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
        with open(character_info_path, "r") as f:
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



def get_wav_from_text_api(text, top_k=20, top_p=0.6, temperature=0.6):
    
    # 加载环境配置
    config = load_infer_config(f"trained/{character_name}/infer_config.json")
    
    # 从配置中提取参数
    ref_wav_path = config['ref_wav_path']
    prompt_text = config['prompt_text']
    prompt_language = config['prompt_language']
    text_language = config['text_language']

    # 调用原始的get_tts_wav函数
    # 注意：这里假设get_tts_wav函数及其所需的其它依赖已经定义并可用
    return get_tts_wav(ref_wav_path, prompt_text, prompt_language, text, text_language, top_k=top_k, top_p=top_p, temperature=temperature)


def test_audio_save():
    fs, audio_to_save=get_wav_from_text_api("""大家好我是查特
花儿不哭大佬开源了一个人工智能语音合成项目
效果相当不错""")
    file_path = "testaudio/example_audio.wav"
    from scipy.io.wavfile import write
    write(file_path, fs, audio_to_save)

# test_audio_save()