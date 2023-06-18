#!/bin/bash

celery --app=src.celery_main:celery worker -l INFO