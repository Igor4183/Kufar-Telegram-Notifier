//
//  logger.hpp
//  Kufar Telegram Notifier
//
//  Created by Macintosh on 27.07.2026.
//

#ifndef logger_hpp
#define logger_hpp

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>

enum class LogLevel{
    info, 
    warning,
    error,
    debug
};

class LogStream{
private:
    std::stringstream buffer;
    LogLevel level;

public:
    LogStream(LogLevel level);

    template<typename T>
    LogStream& operator<<(const T& value){
        buffer << value;
        return *this;
    }

    ~LogStream();
};

class Logger{
private:
    static std::string path;
    static std::string fileName;
    static std::ofstream file;

public:
    static void init();
    static std::string levelToString(LogLevel level);
    static void write(const std::string& text, LogLevel level);

    static LogStream info();
    static LogStream warning();
    static LogStream error();
    static LogStream debug();
};



#endif