FROM python:3.9
ENV PYTHONUNBUFFERED 1

# 1. install pipenv and create an entrypoint
RUN pip install pipenv

# 2. install system level dependencies
# <-- system level dependencies here

# 3. don't run as root
#RUN groupadd --gid 1001 app
#RUN useradd --uid 1001 --gid app --home /app app
#RUN mkdir /app && \
#    chown app.app /app
#USER app
WORKDIR /app/app

# 4. copy the Pipfile and install it
COPY Pipfile /app/Pipfile
RUN pipenv lock -r >> requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 5. add your own code
# <--- own code here

#COPY . /app/app

ENV FLASK_ENV=development
CMD flask run --host=0.0.0.0