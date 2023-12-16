#!/bin/bash

# Detect OS
OS_TYPE=$(uname -s)

# Function to install PostgreSQL for Linux
install_postgresql_linux() {
    echo "Installing PostgreSQL..."
    wget -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc > ACCC4CF8.asc
    sudo mv ACCC4CF8.asc /etc/apt/trusted.gpg.d/
    sudo apt update
    sudo apt install -y postgresql-14

    # Set up a new superuser and database
    sudo -u postgres createuser --superuser $USER
    sudo -u postgres createdb $USER
    sudo -u postgres createdb conversations

    echo "PostgreSQL has been installed."
}

install_pg_vector_linux() {
    # Install pgvector extension
    echo "Installing PGVector..."
    sudo apt install -y git make gcc libpq-dev postgresql-server-dev-14
    git clone https://github.com/pgvector/pgvector.git
    cd pgvector
    make
    sudo make install
    pip3 install pgvector
    cd ..
    echo "PGVector have been installed."
}

# Function to install PostgreSQL for macOS
install_postgresql_mac() {
    echo "Installing PostgreSQL for macOS..."
    brew install postgresql@14
    brew services start postgresql

    # Install development tools
    xcode-select --install
    brew install postgresql@14

    echo "PostgreSQL has been installed for macOS."
}

install_pg_vector_mac() {
    # Clone and build pgvector
    echo "Installing PGVector for macOS..."
    brew install pgvector
    pip3 install pgvector
    echo "PGVector has been installed for macOS."
}

# Function to install Redis for Linux
install_redis_linux() {
    echo "Installing Redis..."
    sudo apt install -y redis-server
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
    echo "Redis has been installed and started."
}

# Function to install Redis for macOS
install_redis_mac() {
    echo "Installing Redis for macOS..."
    brew install redis
    brew services start redis
    echo "Redis has been installed and started for macOS."
}

# Install core dependencies
echo "Installing core dependencies..."
pip3 -v install vosk
pip3 install sounddevice
pip3 install tiktoken
pip install google-cloud-texttospeech
pip install pyttsx3
if [ "$OS_TYPE" = "Darwin" ]; then
    pip3 install pyobjc==9.0.1
fi
pip install SQLAlchemy
pip install psycopg2-binary
pip install celery redis
pip install openai
pip3 install asyncio
pip3 install websockets

# Install system-specific dependencies
if [ "$OS_TYPE" = "Linux" ]; then
    sudo apt install -y libportaudio2
    sudo apt install -y espeak
    sudo apt install -y ffmpeg
elif [ "$OS_TYPE" = "Darwin" ]; then
    brew install portaudio
    brew install ffmpeg
fi

# Ask to install PostgreSQL
if ! command -v psql &> /dev/null
then
    read -p "Would you like to install PostgreSQL? [Y/n]: " install_pgsql
    if [ "$install_pgsql" != "${install_pgsql#[Yy]}" ] ;then
        if [ "$OS_TYPE" = "Linux" ]; then
            install_postgresql_linux
        elif [ "$OS_TYPE" = "Darwin" ]; then
            install_postgresql_mac
        fi
    fi
fi

# Ask to install pgvector
read -p "Would you like to install pgvector if it is not already installed? PGVector is a PostgreSQL extension to facilitate vector similarity querying.[Y/n]: " install_pgvector
if [ "$install_pgvector" != "${install_pgvector#[Yy]}" ] ;then
    if [ "$OS_TYPE" = "Linux" ]; then
        install_pg_vector_linux
    elif [ "$OS_TYPE" = "Darwin" ]; then
        install_pg_vector_mac
    fi
fi

# Ask to install Redis
if ! command -v redis-server &> /dev/null
then
    read -p "Would you like to install Redis if you do not already have it installed? This is required to facilitate long running background tasks as needed. [Y/n]: " install_redis
    if [ "$install_redis" != "${install_redis#[Yy]}" ] ;then
        if [ "$OS_TYPE" = "Linux" ]; then
            install_redis_linux
        elif [ "$OS_TYPE" = "Darwin" ]; then
            install_redis_mac
        fi
    fi
fi


# Configure OpenAI API Key
read -p "Would you like to add your OpenAI API key to .bashrc or .zshrc (for macOS)? [Y/n]: " add_openai_key
if [ "$add_openai_key" != "${add_openai_key#[Yy]}" ] ;then
    read -p "Enter your OpenAI API key: " openai_key
    if [ "$OS_TYPE" = "Linux" ]; then
        echo "export OPENAI_API_KEY='$openai_key'" >> $HOME/.bashrc
    elif [ "$OS_TYPE" = "Darwin" ]; then
        echo "export OPENAI_API_KEY='$openai_key'" >> $HOME/.zshrc
    fi
    echo "OpenAI API key added to shell configuration."
fi

echo "Installation and setup complete."
