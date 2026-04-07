import cv2
import numpy as np
from PIL import Image
import io
import gc  # 引入垃圾回收模块

def process_id_photo(image_bytes, color):
    """
    处理证件照：抠图 + 换底
    """
    input_image = None
    output_image = None
    result_buffer = None
    
    try:
        # --- 1. 图片预处理与压缩 (关键优化点) ---
        # 使用 PIL 打开原始图片
        input_image = Image.open(io.BytesIO(image_bytes))
        
        # 如果是 PNG 且有透明度，先转为白色底，防止后续处理出错
        if input_image.format == 'PNG':
            background = Image.new('RGB', input_image.size, (255, 255, 255))
            if input_image.mode == 'RGBA':
                background.paste(input_image, mask=input_image.split()[3])
                input_image = background
        
        # 【核心优化】如果图片过大，先进行缩小
        # 证件照通常不需要 4000px 的宽度，限制在 2000px 足以保证清晰度
        max_width = 1000
        if input_image.width > max_width:
            ratio = max_width / input_image.width
            new_height = int(input_image.height * ratio)
            input_image = input_image.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # 将处理后的图片转回 bytes，减少后续 cv2 的内存压力
        img_byte_arr = io.BytesIO()
        input_image.save(img_byte_arr, format='JPEG', quality=90)
        img_bytes = img_byte_arr.getvalue()

        # --- 2. 调用 rembg 进行抠图 ---
        # 注意：这里直接传入压缩后的 bytes
        from rembg import remove
        
        # 这里的 remove 会自动处理模型加载，但内存占用依然较高
        output_image = remove(img_bytes)
        
        # --- 3. 换底逻辑 ---
        # 将抠图结果转为 PIL 对象
        result_pil = Image.open(io.BytesIO(output_image))
        
        # 创建背景色
        # 解析颜色字符串，例如 "255,0,0" -> (255, 0, 0)
        try:
            bg_color = tuple(map(int, color.split(',')))
        except:
            bg_color = (255, 255, 255) # 默认白色
            
        background = Image.new('RGB', result_pil.size, bg_color)
        
        # 合成图片 (使用 alpha 通道作为 mask)
        if result_pil.mode == 'RGBA':
            background.paste(result_pil, mask=result_pil.split()[3])
        else:
            background.paste(result_pil)

        # --- 4. 输出结果 ---
        result_buffer = io.BytesIO()
        background.save(result_buffer, format='JPEG', quality=85)
        return result_buffer.getvalue()

    except Exception as e:
        print(f"处理出错: {e}")
        # 出错时返回原始图片或者抛出异常，视业务逻辑而定
        raise e
        
    finally:
        # --- 5. 强制内存清理 (关键优化点) ---
        # 显式删除大对象
        del input_image
        del output_image
        del img_bytes
        if result_buffer:
            del result_buffer
            
        # 强制运行垃圾回收器
        # 在 512MB 环境下，这一步至关重要
        gc.collect()
