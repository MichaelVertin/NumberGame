#!/bin/bash

pm2 delete website
pm2 start app.py --name website


