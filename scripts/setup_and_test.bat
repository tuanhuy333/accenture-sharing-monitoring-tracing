@echo off
echo ================================================================================
echo SETUP AND TEST REAL FLOW SCENARIO
echo ================================================================================
echo.

echo 1. Restarting services with new code...
docker-compose restart order-service payment-service

echo.
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

echo.
echo 2. Running real flow test (Request -^> Error -^> Trace -^> Logs -^> Dashboard)...
python tests\test_real_flow.py

echo.
echo ================================================================================

