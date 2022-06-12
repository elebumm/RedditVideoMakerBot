#!/bin/sh

function install_fail() {
    echo "Installation failed"
    exit 1
}


function Help(){
    echo "Usage: install.sh [option]"
    echo "Options:"
    echo "  -h: Show this help message and exit"
    echo "  -d: Install only dependencies"
    echo "  -p: Install only python dependencies (including playwright)"
}



while getopts ":hydp" option; do
    case $option in
        h)
            Help
            exit 0;;
        y)
            ASSUME_YES=1;;
        d)
            DEPS_ONLY=1;;
        p)
            PYTHON_ONLY=1;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            Help
            exit 1;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            Help
            exit 1;;
    esac
done



function install_macos(){
    if [ ! command -v brew &> /dev/null ]; then
        NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh)"
        if [[ uname -m == "x86_64" ]]; then
            echo "export PATH=/usr/local/bin:$PATH" >> ~/.bash_profile && source ~/.bash_profile
        else
            echo "export PATH=/opt/homebrew/bin:$PATH" >> ~/.bash_profile && source ~/.bash_profile
        fi
    else
        echo "Homebrew is already installed"
    fi
    echo "Installing python"
    if [ ! command -v python3 &> /dev/null ]; then
        brew install python@3.10
    else
        echo "Python is already installed"
    fi    
}

function install_arch(){
    echo "Installing python"
    if [ ! command -v python3 &> /dev/null ]; then
        sudo pacman -S python-pip
    else
        echo "Python is already installed"
    fi
    if [ ! command -v git &> /dev/null ]; then
        sudo pacman -S git
    else
        echo "Git is already installed"
    fi
}

function install_deb(){
    echo "Installing python"
    if [ ! command -v python3 &> /dev/null ]; then
        sudo apt-get install python3
    else
        echo "Python is already installed"
    fi
    if [ ! command -v pip3 &> /dev/null ]; then
        sudo apt-get install python3-pip
    else
        echo "pip is already installed"
    fi
    if [ ! command -v git &> /dev/null ]; then
        sudo apt-get install git
    else
        echo "git is already installed"
    fi
}

function install_fedora(){
    echo "Installing python"
    if [ ! command -v python3 &> /dev/null ]; then
        sudo dnf install python3
    else
        echo "Python is already installed"
    fi
    if [ ! command -v pip3 &> /dev/null ]; then
        sudo dnf install python3-pip
    else
        echo "pip is already installed"
    fi
    if [ ! command -v git &> /dev/null ]; then
        sudo dnf install git
    else
        echo "git is already installed"
    fi
}

function install_centos(){
    echo "Installing python"
    if [ ! command -v python3 &> /dev/null ]; then
        sudo yum install python3
    else
        echo "Python is already installed"
    fi
    if [ ! command -v pip3 &> /dev/null ]; then
        sudo yum install python3-pip
    else
        echo "pip is already installed"
    fi
    if [ ! command -v git &> /dev/null ]; then
        sudo yum install git
    else
        echo "git is already installed"
    fi
}

function get_the_bot(){
    echo "Downloading the bot"
    git clone https://github.com/elebumm/RedditVideoMakerBot.git
}

function install_python_dep(){
    echo "Installing python dependencies"
    cd RedditVideoMakerBot
    pip3 install -r requirements.txt
}

function install_playwright(){
    echo "Installing playwright"
    cd RedditVideoMakerBot
    python3 -m playwright install
    python3 -m playwright install-deps
}

install_deps(){
    if [ "$(uname)" == "Darwin" ]; then
        install_macos || install_fail
    elif [ "$(uname)" == "Linux" ]; then
        if [ "$(cat /etc/os-release | grep -i "arch")" ]; then
            install_arch || install_fail
        elif [ "$(cat /etc/os-release | grep -i "debian")" ]; then
            install_deb || install_fail
        elif [ "$(cat /etc/os-release | grep -i "fedora")" ]; then
            install_fedora || install_fail
        elif [ "$(cat /etc/os-release | grep -i "centos")" ]; then
            install_centos || install_fail
        else
            printf "Your OS is not supported\n Please install python3, pip3 and git manually\n After that, run the script again with the -p option to install python and playwright dependencies\n If you want to add support for your OS, please open a pull request on github\n https://github.com/elebumm/RedditVideoMakerBot"
        fi
    fi
}


function install_main(){
    echo "Installing dependencies..."
    if [[ ASSUME_YES -eq 1 ]]; then
        echo "Assuming yes"
    else
        echo "Continue? (y/n)"
        read answer
        if [ "$answer" != "y" ]; then
            echo "Aborting"
            exit 1
        fi
    fi
    if [[ DEPS_ONLY -eq 1 ]]; then
        echo "Installing only dependencies"
        install_deps
    elif [[ PYTHON_ONLY -eq 1 ]]; then
        echo "Installing only python dependencies"
        install_python_dep
        install_playwright
    else
        echo "Installing dependencies and python dependencies"
        install_deps
        get_the_bot
        install_python_dep
    fi
}

# Run the main function
install_main