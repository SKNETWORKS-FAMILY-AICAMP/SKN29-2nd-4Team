### 결과서
- [데이터 전처리 결과서](reports/1_data_preprocessing_report.md)
- [모델 학습 결과서](reports/2_model_training_report.md)
- [모델 메타데이터](reports/3_model_metadata.md)

---

### 실행 방법
```
# 콘다 환경 통일
conda env create -f environment.yml
conda activate skn2nd

# .env.sample 참고 .env 파일 생성
# back/sql 참고 DB 룩업 테이블 생성

# 하단 GoogleDrive-models 참고
# back/models 경로에 모델 pkl 파일 추가

# FastAPI실행
unicorn back.app.main:app

# streamlit 실행
python -m streamlit run front/app.py
```
[GoogleDrive-models](https://drive.google.com/drive/folders/1pAmWlBoEVxiQ_WKY4FSxfizFR6jLmMRM?usp=sharing)