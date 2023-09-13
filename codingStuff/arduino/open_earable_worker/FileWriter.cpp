#include "FileWriter.h"

FileWriter::FileWriter() {
    sd = new SdExFat();
}

FileWriter::~FileWriter() {
    delete sd;
}

bool FileWriter::begin() {
    return sd->begin(SPI_CC, SPI_SPEED);
}

void FileWriter::end() {
    closeFile();
    sd->end();
}

void FileWriter::cleanFile() {
    sd->remove(_name);
}

void FileWriter::setName(String name) {
    closeFile();
    _name = std::move(name);
}

void FileWriter::openFile() {
    if (_is_open) return;
    int randSuffix = random(1, 10001);  // Generate a random integer between 1 and 10000
    String new_name = String(_name) + "_" + String(randSuffix);  // Append suffix

    file = sd->open(new_name.c_str(), FILE_WRITE);  // Use c_str() to convert to const char*
    // file = sd->open(_name, FILE_WRITE);  // Use c_str() to convert to const char*
    _is_open = true;
}

void FileWriter::closeFile() {
    if (!_is_open) return;
    file.close();
    _is_open = false;
}

bool FileWriter::write_block(uint8_t *block, int size) {
    if (!file) return false;
    file.write(block, size);
    return true;
}

void FileWriter::contained_write_block(uint8_t *block, int size) {
    openFile();
    file.write(block, size);
    closeFile();
}
