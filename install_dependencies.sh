#!/bin/bash

# Function to install PostgreSQL
install_postgresql() {
    echo "Installing PostgreSQL..."
    wget -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc > ACCC4CF8.asc
    sudo mv ACCC4CF8.asc /etc/apt/trusted.gpg.d/
    sudo apt update
    sudo apt install -y postgresql-14

    # Set up a new superuser and database
    sudo -u postgres createuser --superuser $USER
    sudo -u postgres createdb $USER
    sudo -u postgres createdb conversations

    # Install pgvector extension
    sudo apt install -y git make gcc libpq-dev postgresql-server-dev-14
    git clone https://github.com/pgvector/pgvector.git
    cd pgvector
    make
    sudo make install
    pip install pgvector
    cd ..
    echo "PostgreSQL and pgvector have been installed."
}

# Function to install Redis
install_redis() {
    echo "Installing Redis..."
    sudo apt install -y redis-server
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
    echo "Redis has been installed and started."
}

# Install core dependencies
echo "Installing core dependencies..."
pip3 -v install vosk
pip install sounddevice
sudo apt install -y libportaudio2
pip3 install tiktoken
pip install google-cloud-texttospeech
pip install pyttsx3
sudo apt install -y espeak
sudo apt install -y ffmpeg
pip install SQLAlchemy
pip install psycopg2-binary
pip install celery redis

# Ask to install PostgreSQL
read -p "Would you like to install the PostgreSQL database if you do not already have it installed? This will also configure pgvector for you for similarity querying. Once complete, remember to add your credentials to the config.py file using the DATABASE_CONFIG setting. [Y/n]: " install_pgsql
if [ "$install_pgsql" != "${install_pgsql#[Yy]}" ] ;then
    install_postgresql
fi

# Ask to install Redis
read -p "Would you like to install Redis if you do not already have it installed? This is required to facilitate long running background tasks as needed. [Y/n]: " install_redis
if [ "$install_redis" != "${install_redis#[Yy]}" ] ;then
    install_redis
fi

# Configure OpenAI API Key
read -p "Would you like to add your OpenAI API key to .bashrc? [Y/n]: " add_openai_key
if [ "$add_openai_key" != "${add_openai_key#[Yy]}" ] ;then
    read -p "Enter your OpenAI API key: " openai_key
    echo "export OPENAI_API_KEY='$openai_key'" >> $HOME/.bashrc
    echo "OpenAI API key added to .bashrc"
fi

echo "Installation and setup complete."
