from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def test_eduqg():
    model_name = "iarfmoose/t5-base-question-generator"

    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    # Dummy data
    context = "The mitochondria is the powerhouse of the cell."
    answer = "mitochondria"

    input_text = f"<answer> {answer} <context> {context}"
    inputs = tokenizer(input_text, return_tensors="pt")

    print("Generating question...")
    outputs = model.generate(**inputs, max_length=64, num_beams=4)
    question = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print("\nGenerated Question:")
    print(question)

if __name__ == "__main__":
    test_eduqg()
