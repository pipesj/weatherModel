FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY app.py ${LAMBDA_TASK_ROOT}
COPY solarRadModel.pkl ${LAMBDA_TASK_ROOT}
COPY tempModel.pkl ${LAMBDA_TASK_ROOT}

CMD [ "app.handler" ] 
