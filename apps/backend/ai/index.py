from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class AIService:
    def __init__(self):
        """
        Hugging Face의 transformers 라이브러리를 사용하여
        무료 오픈 소스 모델(microsoft/DialoGPT-small)을 로드합니다.
        """
        try:
            # 모델과 토크나이저를 로드합니다.
            # 처음 실행 시 모델 파일을 다운로드하므로 시간이 걸릴 수 있습니다.
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
            self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
            print("AI model (DialoGPT-small) loaded successfully.")
        except Exception as e:
            print(f"Error loading AI model: {e}")
            self.tokenizer = None
            self.model = None

    async def generate_stream_response(self, user_message: str, history: list):
        """
        DialoGPT 모델을 사용하여 사용자 메시지에 대한 응답을 생성합니다.
        스트리밍을 흉내 내기 위해 전체 응답을 한 번에 생성하고, 단어 ���위로 반환합니다.
        """
        if not self.model or not self.tokenizer:
            error_message = "AI model is not available."
            for word in error_message.split():
                yield word + " "
            return

        try:
            # 1. 채팅 히스토리 인코딩
            # DialoGPT는 대화의 각 턴 끝에 EOS 토큰을 추가해야 합니다.
            history_ids = [
                self.tokenizer.encode(msg.content + self.tokenizer.eos_token, return_tensors="pt")
                for msg in history if msg.role in ["user", "assistant"]
            ]
            
            # 2. 현재 사용자 메시지 추가
            new_user_input_ids = self.tokenizer.encode(user_message + self.tokenizer.eos_token, return_tensors="pt")
            
            # 3. 모든 텐서를 하나로 결합
            bot_input_ids = torch.cat(history_ids + [new_user_input_ids], dim=-1) if history_ids else new_user_input_ids

            # 4. 모델을 사용하여 응답 생성
            chat_history_ids = self.model.generate(
                bot_input_ids,
                max_length=1000,
                pad_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3,
                do_sample=True,
                top_k=100,
                top_p=0.7,
                temperature=0.8
            )

            # 5. 생성된 응답에서 마지막 부분(AI의 답변)만 디코딩
            response_text = self.tokenizer.decode(
                chat_history_ids[:, bot_input_ids.shape[-1]:][0],
                skip_special_tokens=True
            )

            # 6. 스트리밍처럼 단어 단위로 응답 반환
            if not response_text.strip():
                response_text = "I'm not sure how to respond to that."

            for word in response_text.split():
                yield word + " "

        except Exception as e:
            error_message = f"Error during AI response generation: {e}"
            print(error_message)
            for word in error_message.split():
                yield word + " "
