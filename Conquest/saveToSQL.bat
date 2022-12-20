@echo off
call activate base
call cd python
call python saveToSQL.py %1
cd ..