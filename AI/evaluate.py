# Model results
results = [
    ("lily1.png", "REAL", "FAKE"),
    ("real1.jpg", "REAL", "FAKE"),
    ("sky1.jpeg", "REAL", "FAKE"),
    ("fake1.jpeg", "SYNTHETIC", "FAKE"),
    ("lily2.jpeg", "SYNTHETIC", "FAKE"),
    ("sky2.jpeg", "SYNTHETIC", "FAKE"),
]

correct = 0

for image, actual, prediction in results:
    if actual == "REAL" and prediction == "REAL":
        correct += 1
    elif actual == "SYNTHETIC" and prediction == "FAKE":
        correct += 1

accuracy = correct / len(results) * 100

print("================================")
print("     VERITRACE EVALUATION")
print("================================")
print(f"Total Images : {len(results)}")
print(f"Correct      : {correct}")
print(f"Accuracy     : {accuracy:.2f}%")
print("================================")