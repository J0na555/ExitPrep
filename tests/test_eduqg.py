from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def test_eduqg():
    model_name = "iarfmoose/t5-base-question-generator"

    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    # Dummy data
    context = "The capital city of France is Paris, known for its cultural landmarks and museums."
    answer = "Paris"
    context = "The largest planet in our solar system is a gas giant with a prominent Great Red Spot."
    answer = "Jupiter"
    context = "The programming language known for its use in web development and created by Brendan Eich is JavaScript."
    answer = "JavaScript"

    input_text = f"<answer> {answer} <context> {context}"
    inputs = tokenizer(input_text, return_tensors="pt")

    print("Generating question...")
    outputs = model.generate(**inputs, max_length=64, num_beams=4)
    question = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print("\nGenerated Question:")
    print(question)

if __name__ == "__main__":
    test_eduqg()
