//
//  main.cpp
//  Kufar Telegram Notifier
//
//  Created by Macintosh on 02.06.2022.
//  Updated by another Macintosh on 13.07.2026
//

#include <iostream>
#include <unistd.h>
#include <signal.h>
#include <fstream>
#include <vector>
#include <map>

#include "json.hpp"
#include "kufar.hpp"
#include "telegram.hpp"
#include "networking.hpp"
#include "helperfunctions.hpp"
#include "logger.hpp"

using namespace std;
using namespace Kufar;
using namespace Telegram;
using nlohmann::json;

const string CACHE_FILE_NAME = "cached-data.json";
const string CONFIGURATION_FILE_NAME = "kufar-configuration.json";

struct ConfigurationFile {
    string path;
    json contents;
};

struct CacheFile {
    string path;
    json contents;
};

struct Files {
    ConfigurationFile configuration;
    CacheFile cache;
};

struct ProgramConfiguration {
    vector<KufarConfiguration> kufarConfiguration;
    TelegramConfiguration telegramConfiguration;
    Files files;
    
    int queryDelaySeconds = 5;
    int loopDelaySeconds = 30;
};

void loadJSONConfigurationData(const json &data, ProgramConfiguration &programConfiguration) {
    {
        json telegramData = data.at("telegram");
        programConfiguration.telegramConfiguration.botToken = telegramData.at("bot-token");
        programConfiguration.telegramConfiguration.chatID = telegramData.at("chat-id");
    }
    {
        json queriesData = data.at("queries");
        for (const json &query : queriesData) {
            KufarConfiguration kufarConfiguration;
            
            kufarConfiguration.onlyTitleSearch = getOptionalValue<bool>(query, "only-title-search");
            kufarConfiguration.tag = getOptionalValue<string>(query, "tag");
            if (query.contains("price")) {
                json queryPriceData = query.at("price");
                kufarConfiguration.priceRange.priceMin = getOptionalValue<int>(queryPriceData, "min");
                kufarConfiguration.priceRange.priceMax = getOptionalValue<int>(queryPriceData, "max");
            }
            
            kufarConfiguration.language = getOptionalValue<string>(query, "language");
            kufarConfiguration.limit = getOptionalValue<int>(query, "limit");
            kufarConfiguration.currency = getOptionalValue<string>(query, "currency");
            kufarConfiguration.condition = getOptionalValue<ItemCondition>(query, "condition");
            kufarConfiguration.sellerType = getOptionalValue<SellerType>(query, "seller-type");
            kufarConfiguration.kufarDeliveryRequired = getOptionalValue<bool>(query, "kufar-delivery-required");
            kufarConfiguration.kufarPaymentRequired = getOptionalValue<bool>(query, "kufar-payment-required");
            kufarConfiguration.kufarHalvaRequired = getOptionalValue<bool>(query, "kufar-halva-required");
            kufarConfiguration.onlyWithPhotos = getOptionalValue<bool>(query, "only-with-photos");
            kufarConfiguration.onlyWithVideos = getOptionalValue<bool>(query, "only-with-videos");
            kufarConfiguration.onlyWithExchangeAvailable = getOptionalValue<bool>(query, "only-with-exchange-available");
            kufarConfiguration.sortType = getOptionalValue<SortType>(query, "sort-type");
            kufarConfiguration.category = getOptionalValue<Category>(query, "category");
            kufarConfiguration.subCategory = getOptionalValue<int>(query, "sub-category");
            kufarConfiguration.region = getOptionalValue<Region>(query, "region");
            kufarConfiguration.areas = getOptionalValue<vector<int>>(query, "areas");
            kufarConfiguration.chatID = getOptionalValue<string>(query, "chat-id");
            kufarConfiguration.trackingStartTime = getOptionalValue<time_t>(query, "start-time");
            programConfiguration.kufarConfiguration.push_back(kufarConfiguration);
        }
    }
    {
        if (data.contains("delays")) {
            json delaysData = data.at("delays");
            programConfiguration.queryDelaySeconds = delaysData.at("query");
            programConfiguration.loopDelaySeconds = delaysData.at("loop");
        }
    }
}

// edit by ChatGPT
void printJSONConfigurationData(const ProgramConfiguration &programConfiguration) {
    std::stringstream ss;

    ss << "- Telegram:\n"
       << "\t- Токен: " << programConfiguration.telegramConfiguration.botToken << "\n"
       << "\t- ID Чата: " << programConfiguration.telegramConfiguration.chatID << "\n\n"
       << "- Запросы:\n";

    for (const auto &query : programConfiguration.kufarConfiguration) {
        ss << "\t- Название: " << query.tag << "\n"
           << "\t- Чат, в который будет отправлено сообщение: " << query.chatID << "\n"
           << "\t- Отравлять сообщения у которых дата не раньше: "
           << (query.trackingStartTime ? ctime(&query.trackingStartTime.value()) : PROPERTY_UNDEFINED.c_str())
           << "\t- Поиск только по заголовку: " << query.onlyTitleSearch << "\n"
           << "\t- Цена:\n"
           << "\t\t- Минимальная: " << query.priceRange.priceMin << " BYN\n"
           << "\t\t- Максимальная: " << query.priceRange.priceMax << " BYN\n"
           << "\t- Язык: " << query.language << "\n"
           << "\t- Макс. кол-во объявлений за один запрос: " << query.limit << "\n"
           << "\t- Валюта: " << query.currency << "\n"
           << "\t- Состояние: "
           << (query.condition ? EnumString::itemCondition(*query.condition) : PROPERTY_UNDEFINED)
           << "\n"
           << "\t- Продавец: "
           << (query.sellerType ? EnumString::sellerType(*query.sellerType) : PROPERTY_UNDEFINED)
           << "\n"
           << "\t- Только с Kufar Доставкой: " << query.kufarDeliveryRequired << "\n"
           << "\t- Только с Kufar Оплатой: " << query.kufarPaymentRequired << "\n"
           << "\t- Только с Kufar Рассрочкой (Халва): " << query.kufarPaymentRequired << "\n" // Сейчас там выводится Kufar Оплата, а не Рассрочка.
           << "\t- Только с фото: " << query.onlyWithPhotos << "\n"
           << "\t- Только с видео: " << query.onlyWithVideos << "\n"
           << "\t- Только с возможностью обмена: " << query.onlyWithExchangeAvailable << "\n"
           << "\t- Тип сортировки: "
           << (query.sortType ? EnumString::sortType(*query.sortType) : PROPERTY_UNDEFINED)
           << "\n"
           << "\t- Категория: "
           << (query.category ? EnumString::category(*query.category) : PROPERTY_UNDEFINED)
           << "\n"
           << "\t- Подкатегория: "
           << (query.subCategory ? EnumString::subCategory(*query.subCategory) : PROPERTY_UNDEFINED)
           << "\n"
           << "\t- Город: "
           << (query.region ? EnumString::region(*query.region) : PROPERTY_UNDEFINED)
           << "\n"
           << "\t- Район: ";

        if (query.areas) {
            for (size_t i = 0; i < query.areas->size(); i++) {
                ss << EnumString::area((*query.areas)[i]);

                if (i + 1 < query.areas->size()) {
                    ss << ", ";
                }
            }
        } else {
            ss << PROPERTY_UNDEFINED;
        }

        ss << "\n\n";
    }

    ss << "- Задержки:\n"
       << "\t- Перед новым запросом: " << programConfiguration.queryDelaySeconds << "с. \n"
       << "\t- После прохода всего списка запросов: " << programConfiguration.loopDelaySeconds << "c.";

    Logger::info() << ss.str();
}

json getJSONDataFromPath(const string &JSONFilePath) {
    Logger::info() << "[Загрузка файла]: " << '"' << JSONFilePath << '"';

    if (!fileExists(JSONFilePath)){
        Logger::error() << "Файл не существует по данному пути или к нему нет доступа.";
        exit(1);
    }
    
    if (getFileSize(JSONFilePath) > 4000000) {
        Logger::error() << "Размер файла превышает 4МБ.";
        exit(1);
    }
        
    try {
       json textFromFile = json::parse(getTextFromFile(JSONFilePath));
       return textFromFile;
    } catch (const exception &exc) {
       Logger::error() << "Невозможно получить данные из файла " << '"' << JSONFilePath << '"';
       Logger::error() << "::: " << exc.what() << " :::";
       exit(1);
    }

}

const string prefixConfigurationFile = "--config=";
const string prefixCacheFile = "--cache=";

/**
  Загрузка файлов:
  kufar-configuration.json,
  cached-data.json
 */

Files getFiles(const int &argsCount, char **args) {
    Files files;
    
    for (int i = 0; i < argsCount; i++){
        string currentArgument = args[i];
        
        if(stringHasPrefix(currentArgument, prefixConfigurationFile)) { // --config="path"
            currentArgument.erase(0, prefixConfigurationFile.length());
            files.configuration.path = currentArgument;
        } else if (stringHasPrefix(currentArgument, prefixCacheFile)) { // --cache="path"
            currentArgument.erase(0, prefixCacheFile.length());
            files.cache.path = currentArgument;
        }
        
    }
    
    if (files.configuration.path.empty() || files.cache.path.empty()) {
        optional<string> applicationDirectory = getWorkingDirectory();
        
        if (!applicationDirectory.has_value()) {
            Logger::error() << "Невозможно автоматически определить путь к текущей папке. Передайте файл конфигурации/кеша в виде аргумента.";
            exit(1);
        }
        
        if (files.configuration.path.empty()) {
            files.configuration.path = applicationDirectory.value() + PATH_SEPARATOR + ".." + PATH_SEPARATOR + "data" + PATH_SEPARATOR + CONFIGURATION_FILE_NAME;
        }
        
        if (files.cache.path.empty()) {
            files.cache.path = applicationDirectory.value() + PATH_SEPARATOR + ".." + PATH_SEPARATOR + "data" + PATH_SEPARATOR + CACHE_FILE_NAME;
        }
    }
    
    files.configuration.contents = getJSONDataFromPath(files.configuration.path);
    files.cache.contents = getJSONDataFromPath(files.cache.path);
    
    return files;
}

int main(int argc, char **argv) {
    ProgramConfiguration programConfiguration;
    map<string, vector<string>> viewedAds;

    Logger::init();

    try{
        viewedAds = programConfiguration.files.cache.contents.get<map<string, vector<string>>>();
    }
    catch (const exception &exc) { // not error
        Logger::warning() << "(Failed to get cache data, but programConfiguration parameter may not be defined.) " << exc.what();
    }

    bool flag = true;
    while (true) {
        // Logger::info() << "начало обновления уведомлений";
        programConfiguration.files = getFiles(argc, argv);
        loadJSONConfigurationData(programConfiguration.files.configuration.contents, programConfiguration);
        Logger::info() << "Обновлён kufar-configuration.json";
        if (flag){
            flag = false;
            printJSONConfigurationData(programConfiguration);
        }
        // DEBUG_MSG(printJSONConfigurationData(programConfiguration));
        
        for (auto requestConfiguration : programConfiguration.kufarConfiguration) {
            unsigned int sentCount = 0;
            
            try {
                for (const auto &advert : getAds(requestConfiguration)) {
                    string curChatID = (advert.chatID.empty() ? programConfiguration.telegramConfiguration.chatID : advert.chatID);
                    if (!vectorContains(viewedAds[curChatID], advert.id)) {
                        if (advert.date < requestConfiguration.trackingStartTime) { 
                            Logger::info() << "[FILTER]: Not sent, ad too old [Title: " << advert.title << "], [Kufar_ID: " << advert.id << "], [Tag: " << advert.tag << "], [Link: " << advert.link << "], [Chat_id: " << curChatID << "]";
                            continue; 
                        }
                        Logger::info() << "[New]: Adding [Title: " << advert.title << "], [ID: " << advert.id << "], [Tag: " << advert.tag << "], [Link: " << advert.link << "], [Chat_id: " << curChatID << "]";
                        viewedAds[curChatID].push_back(advert.id);
                        sentCount += 1;

                        try {
                            sendAdvert(programConfiguration.telegramConfiguration, advert);
                        } catch (const exception &exc) {
                            Logger::error() << "(sendAdvert): " << exc.what();
                        }
                        
                    } else {
                        //cout << "[Already was!]" << endl;
                    }
                    usleep(300000); // 0.3s
                }
            } catch (const exception &exc) {
                Logger::error() << "(getAds): " << exc.what();
            }
            DEBUG_MSG("(QueryDelay) Sleeping for: " << programConfiguration.queryDelaySeconds << "s.");
            sleep(programConfiguration.queryDelaySeconds);
            
            if (sentCount > 0) {
                saveFile(programConfiguration.files.cache.path, ((json)viewedAds).dump(4));
            }
        }
        DEBUG_MSG("(LoopDelay) Sleeping for: " << programConfiguration.loopDelaySeconds << "s.");

        // Logger::info() << "конец обновления уведомлений";
        sleep(programConfiguration.loopDelaySeconds);
    }
    return 0;
}
