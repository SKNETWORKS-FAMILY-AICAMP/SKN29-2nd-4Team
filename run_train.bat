@echo off
call C:\Users\seokh\miniconda3\Scripts\activate.bat skn2nd
set KMP_DUPLICATE_LIB_OK=TRUE
set MKL_THREADING_LAYER=INTEL
set OMP_NUM_THREADS=4
set MKL_NUM_THREADS=4
python C:\prj2\back\app\ml\rev_03\run.py
pause
