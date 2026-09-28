from genconvit_model import predict_video


VIDEO = "AI/samples/video/real2.mp4"


result = predict_video(
    VIDEO,
    max_frames=15
)

print("\nGenConViT Video Result")
print("----------------------")

for key, value in result.items():
    print(f"{key}: {value}")