#!/bin/bash

echo "=========================================="
echo "ODBC Driver Installation Script"
echo "=========================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "Unsupported operating system: $OSTYPE"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# macOS Installation
if [ "$OS" == "macos" ]; then
    echo "Installing ODBC Driver for macOS..."
    echo ""
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    echo "Adding Microsoft tap..."
    brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release 2>/dev/null
    
    echo "Updating Homebrew..."
    brew update
    
    echo "Installing ODBC Driver 18..."
    HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql18
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ ODBC Driver 18 installed successfully!"
    else
        echo ""
        echo "Installation failed. Trying ODBC Driver 17..."
        HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql17
        
        if [ $? -eq 0 ]; then
            echo "✓ ODBC Driver 17 installed successfully!"
        else
            echo "✗ Installation failed"
            exit 1
        fi
    fi
    
    # Install unixODBC if not present
    brew install unixodbc 2>/dev/null
fi

# Linux Installation
if [ "$OS" == "linux" ]; then
    echo "Installing ODBC Driver for Linux..."
    echo ""
    
    # Detect Linux distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    else
        echo "Cannot detect Linux distribution"
        exit 1
    fi
    
    echo "Distribution: $DISTRO $VERSION"
    echo ""
    
    # Ubuntu/Debian
    if [[ "$DISTRO" == "ubuntu" ]] || [[ "$DISTRO" == "debian" ]]; then
        echo "Setting up Microsoft repository..."
        
        # Add Microsoft GPG key
        curl https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc
        
        # Add repository based on version
        if [[ "$DISTRO" == "ubuntu" ]]; then
            if [[ "$VERSION" == "22.04" ]]; then
                curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
            elif [[ "$VERSION" == "20.04" ]]; then
                curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
            else
                echo "Ubuntu version $VERSION may not be fully supported. Trying 22.04 repository..."
                curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
            fi
        elif [[ "$DISTRO" == "debian" ]]; then
            curl https://packages.microsoft.com/config/debian/11/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
        fi
        
        echo "Updating package list..."
        sudo apt-get update
        
        echo "Installing ODBC Driver 18..."
        sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
        
        if [ $? -ne 0 ]; then
            echo "Failed to install ODBC Driver 18. Trying Driver 17..."
            sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
        fi
        
        echo "Installing unixODBC..."
        sudo apt-get install -y unixodbc-dev
        
        echo "✓ Installation complete!"
    
    # Red Hat/CentOS/Fedora
    elif [[ "$DISTRO" == "rhel" ]] || [[ "$DISTRO" == "centos" ]] || [[ "$DISTRO" == "fedora" ]]; then
        echo "Setting up Microsoft repository..."
        
        sudo curl -o /etc/yum.repos.d/mssql-release.repo https://packages.microsoft.com/config/rhel/8/prod.repo
        
        echo "Removing conflicting packages..."
        sudo yum remove -y unixODBC-utf16 unixODBC-utf16-devel 2>/dev/null
        
        echo "Installing ODBC Driver 18..."
        sudo ACCEPT_EULA=Y yum install -y msodbcsql18
        
        if [ $? -ne 0 ]; then
            echo "Failed to install ODBC Driver 18. Trying Driver 17..."
            sudo ACCEPT_EULA=Y yum install -y msodbcsql17
        fi
        
        echo "Installing unixODBC..."
        sudo yum install -y unixODBC-devel
        
        echo "✓ Installation complete!"
    
    else
        echo "Unsupported Linux distribution: $DISTRO"
        echo "Please install manually from:"
        echo "https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server"
        exit 1
    fi
fi

# Verify installation
echo ""
echo "=========================================="
echo "Verifying Installation"
echo "=========================================="
echo ""

if command -v odbcinst &> /dev/null; then
    echo "Available ODBC drivers:"
    odbcinst -q -d
    echo ""
    
    # Check if SQL Server driver is present
    if odbcinst -q -d | grep -q "SQL Server"; then
        echo "✓ SQL Server ODBC driver is installed!"
        echo ""
        echo "You can now run your application:"
        echo "  python app.py"
    else
        echo "✗ SQL Server ODBC driver not found in the list above"
        echo "Please check the installation logs for errors"
        exit 1
    fi
else
    echo "✗ odbcinst command not found"
    echo "unixODBC may not be installed correctly"
    exit 1
fi

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
