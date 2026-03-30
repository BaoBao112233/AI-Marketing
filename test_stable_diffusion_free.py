import requests

url = "https://gateway.pixazo.ai/getImage/v1/getSDXLImage"
headers = {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
    "Ocp-Apim-Subscription-Key": "YOUR_SUBSCRIPTION_KEY"
}
data = {
    "prompt": "High-resolution, realistic image of a sparrow bird perched on a blooming cherry blossom branch during springtime. The sparrow feathers should be finely detailed with natural colors, including shades of brown and white. The background should be soft-focused with a clear blue sky, creating a serene and peaceful atmosphere.",
    "negative_prompt": "Low-quality, blurry image, with any other birds or animals. Avoid abstract or cartoonish styles, dark or gloomy atmosphere, unnecessary objects or distractions in the background, harsh lighting, and unnatural colors.",
    "height": 1024,
    "width": 1024,
    "num_steps": 20,
    "guidance_scale": 5,
    "seed": 40
}

response = requests.post(url, json=data, headers=headers)
print(response.json())