:: Launch qtlab

cd qtlab
call qtlab.bat
timeout -t 3
cd ..

cd measurement
:: Launch measurement kernel and operator
start Console -w "Measurement console" -r "/k python start.py"


