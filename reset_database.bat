@echo off
title BookBazaar - Reset & Seed Database
color 0E
echo Resetting and Seeding BookBazaar Database...
cd /d "%~dp0"
python manage.py seed_data
echo Done! All test books, sellers, listings and ads are fresh.
pause
