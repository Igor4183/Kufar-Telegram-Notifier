//
//  logger.cpp
//  Kufar Telegram Notifier
//
//  Created by Macintosh on 27.07.2026.
//

#include <chrono>
#include <filesystem>
#include <format>

#include "logger.hpp"

std::string getCurrentTime(){
    auto now = std::chrono::time_point_cast<std::chrono::seconds>(
        std::chrono::system_clock::now()
    );
    return std::format("{:%Y-%m-%d_%H-%M-%S}", now);
}

std::string Logger::path;
std::string Logger::fileName;
std::ofstream Logger::file;

LogStream::LogStream(LogLevel level){
    this->level = level;
}

LogStream::~LogStream(){
    std::string message = buffer.str();
    std::string time = getCurrentTime();
    std::string text = "[" + time + "] [" + Logger::levelToString(level) + "] " + message;
    Logger::write(text, level);
}

void Logger::init(){
    std::filesystem::create_directories("data/logs_cpp/");
    Logger::fileName = getCurrentTime() + ".log";
    Logger::path = "data/logs_cpp/" + Logger::fileName;

    Logger::file.open(Logger::path);
    if (!file.is_open()){
        std::cerr << "Cannot open log file\n";
    }
}

std::string Logger::levelToString(LogLevel level){
    if (level==LogLevel::info) return "INFO";
    if (level==LogLevel::warning) return "WARNING";
    if (level==LogLevel::error) return "ERROR";
    if (level==LogLevel::debug) return "DEBUG";

    return "UNKNOWN";
}

void Logger::write(const std::string& text, LogLevel level){
    if (level == LogLevel::info) std::cout << text << std::endl;
    else std::cerr << text << std::endl;
    if (file.is_open()) file << text << std::endl;
}

LogStream Logger::info(){
    return LogStream(LogLevel::info);
}

LogStream Logger::warning(){
    return LogStream(LogLevel::warning);
}

LogStream Logger::error(){
    return LogStream(LogLevel::error);
}

LogStream Logger::debug(){
    return LogStream(LogLevel::debug);
}


