import requests

url = "https://gateway.pixazo.ai/sd3/v1/getData"
headers = {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
    "Ocp-Apim-Subscription-Key": "Your_API_Key_Here"
}
data = {
    "prompt": "Picture a sleek, futuristic car racing through a neon-lit cityscape, its engine humming efficiently as it blurs past digital billboards. The driver skillfully navigates the glowing streets, aiming for victory in this high-tech, adrenaline-fueled race of tomorrow.",
    "negativePrompt": "dark, blurry",
    "steps": 28,
    "cfg": 4.0,
    "aspect_ratio": "3:2",
    "output_format": "jpg",
    "output_quality": 90,
    "prompt_strength": 0.85
}

response = requests.post(url, json=data, headers=headers)
print(response.json())