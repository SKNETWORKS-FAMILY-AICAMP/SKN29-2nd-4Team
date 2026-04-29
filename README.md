### conda 환경 통일
```
conda create -f environment.yml
conda activate skn2nd
```

### fastapi 실행 방법
```
uvicorn back.app.main:app
```

### streamlit 실행 방법
```
streamlit run front/app.py
```

### pycache, init 파일 숨기기 편의 설정
```
# .vscode/settings.json에 추가
"files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/__init__.py": true
}
```