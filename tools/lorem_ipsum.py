import asyncio
import random

async def run(params: dict):
    paragraphs_count = int(params.get("paragraphs", "3"))
    
    yield {"type": "log", "message": f"Generating {paragraphs_count} paragraphs of dummy text..."}
    await asyncio.sleep(0.3)
    
    words_pool = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua", "ut", "enim", "ad", "minim", "veniam", "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi", "ut", "aliquip", "ex", "ea", "commodo", "consequat", "duis", "aute", "irure", "dolor", "in", "reprehenderit", "in", "voluptate", "velit", "esse", "cillum", "dolore", "eu", "fugiat", "nulla", "pariatur", "excepteur", "sint", "occaecat", "cupidatat", "non", "proident", "sunt", "in", "culpa", "qui", "officia", "deserunt", "mollit", "anim", "id", "est", "laborum"]
    
    try:
        output_paragraphs = []
        for p in range(paragraphs_count):
            sentences = []
            for s in range(random.randint(4, 7)):
                words = [random.choice(words_pool) for _ in range(random.randint(6, 12))]
                # Capitalize first word
                words[0] = words[0].capitalize()
                sentences.append(" ".join(words) + ".")
            para = " ".join(sentences)
            output_paragraphs.append(para)
            yield {"type": "found", "message": f"Paragraph {p+1}:\n{para}\n"}
            
        yield {"type": "success", "message": "Lorem Ipsum generated successfully."}
    except Exception as e:
        yield {"type": "error", "message": f"Generation failed: {str(e)}"}
