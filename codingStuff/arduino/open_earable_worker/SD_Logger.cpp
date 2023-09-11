#include "SD_Logger.h"

#include <utility>

FileWriter * SD_Logger::writer;
char SD_Logger::_buffer[LOGGER_BUFFER_SIZE];
int SD_Logger::_index = 0;

bool SD_Logger::begin() {
    writer = new FileWriter();
    _index = 0;
    bool status = writer->begin();
    writer->cleanFile();
    write_header();
    return status;
}

void SD_Logger::end() {
    writer->end();
    delete writer;
}

void SD_Logger::set_name(String name) {
    writer->setName(std::move(name));
}

void SD_Logger::data_callback(int id, unsigned int timestamp, uint8_t * data) {
    if (id == -1) return dump_to_sd();

    String text = String(id);

    text += "," + String(timestamp);

//    if (r_type == R_TYPE_FLOAT) {
//        text += convert_float((float*)data);
//    } else if (r_type == R_TYPE_INT) {
    text += convert_int((int*)data);
//    }
    text += "\r\n";

    if (text.length() + _index > LOGGER_BUFFER_SIZE) {
        dump_to_sd();
    }
    text.toCharArray(&(_buffer[_index]), text.length());
    _index += text.length() - 1; // -1 to remove null terminator
}

String SD_Logger::convert_float(float *data) {
    String text = "";
    int count = (int)data[0];
    for (int i=0; i<count; i++) {
        text +=  ", " + String(data[i+1]);
    }
    return text;
}

String SD_Logger::convert_int(int *data) {
    String text = "";
    int count = data[0];
    for (int i=0; i<count; i++) {
        text +=  ", " + String(data[i+1]);
    }
    return text;
}

void SD_Logger::dump_to_sd() {
    if (_index == 0) return;
    writer->contained_write_block((uint8_t*)_buffer, _index);
    memset(_buffer, 0, LOGGER_BUFFER_SIZE);
    _index = 0;
}

void SD_Logger::write_header() {
    _index = 0;
    // String header = "ID,TIMESTAMP,Temp01,Temp02,Temp03,Temp04,Temp05,Temp06,ObjTemp01,ObjTemp02,ObjTemp03,ObjTemp04,ObjTemp05,ObjTemp06,ACC_X,ACC_Y,ACC_Z,GYRO_X,GYRO_Y,GYRO_Z,MAG_X,MAG_Y,MAG_Z\n\r";
    String header = "ID,TIMESTAMP,TympanicMembrane,Concha,EarCanal,Out_Bottom,Out_Top,Out_Middle,ObjTympanicMembrane,ObjConcha,ObjEarCanal,ObjOut_Bottom,ObjOut_Top,ObjOut_Middle,ACC_X,ACC_Y,ACC_Z,GYRO_X,GYRO_Y,GYRO_Z,MAG_X,MAG_Y,MAG_Z\n\r";
    header.toCharArray(&(_buffer[_index]), header.length());
    _index += header.length() - 1; // -1 to remove null terminator

    dump_to_sd();
}
