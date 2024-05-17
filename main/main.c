#include <stdio.h>
#include "driver/i2c.h"
#include "esp_log.h"
#include "mpu6050.h"
#include "esp_timer.h"

#define I2C_MASTER_SCL_IO           1       
#define I2C_MASTER_SDA_IO           0       
#define I2C_MASTER_NUM              I2C_NUM_0 
#define I2C_MASTER_FREQ_HZ          100000   

#define MPU6050_ADDR                0x68      
#define MPU6050_PWR_MGMT_1          0x6B      
#define MPU6050_PWR_MGMT_1_RESET    0x00      
#define MPU6050_REGISTER_DATA_START 0x3B      

static const char *TAG = "MPU6050";

void i2c_master_init() {
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_io_num = I2C_MASTER_SCL_IO,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = I2C_MASTER_FREQ_HZ,
    };
    i2c_param_config(I2C_MASTER_NUM, &conf);
    i2c_driver_install(I2C_MASTER_NUM, conf.mode, 0, 0, 0);
}

void mpu6050_init() {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (MPU6050_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, MPU6050_PWR_MGMT_1, true);
    i2c_master_write_byte(cmd, MPU6050_PWR_MGMT_1_RESET, true);
    i2c_master_stop(cmd);

    esp_err_t ret = i2c_master_cmd_begin(I2C_MASTER_NUM, cmd, pdMS_TO_TICKS(1000));
    i2c_cmd_link_delete(cmd);

    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "MPU6050 reset successful");
    } else {
        ESP_LOGE(TAG, "Failed to reset MPU6050: %d", ret);
    }
}

void mpu6050_read_data() {
    uint8_t data[14];
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (MPU6050_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, MPU6050_REGISTER_DATA_START, true);
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (MPU6050_ADDR << 1) | I2C_MASTER_READ, true);
    i2c_master_read(cmd, data, 14, I2C_MASTER_LAST_NACK);
    i2c_master_stop(cmd);

    esp_err_t ret = i2c_master_cmd_begin(I2C_MASTER_NUM, cmd, pdMS_TO_TICKS(1000));
    i2c_cmd_link_delete(cmd);

    if (ret == ESP_OK) {
        int16_t raw_ax = (int16_t)((data[0] << 8) | data[1]);
        int16_t raw_ay = (int16_t)((data[2] << 8) | data[3]);
        int16_t raw_az = (int16_t)((data[4] << 8) | data[5]);
        int16_t raw_gx = (int16_t)((data[8] << 8) | data[9]);
        int16_t raw_gy = (int16_t)((data[10] << 8) | data[11]);
        int16_t raw_gz = (int16_t)((data[12] << 8) | data[13]);

        // Normalize the raw data to understandable units
        const float accel_scale = 16384.0f; // 1g for ±2g sensitivity
        const float gyro_scale = 131.0f; // 1°/s for ±250°/s sensitivity

        float ax = raw_ax / accel_scale;
        float ay = raw_ay / accel_scale;
        float az = raw_az / accel_scale;
        float gx = raw_gx / gyro_scale;
        float gy = raw_gy / gyro_scale;
        float gz = raw_gz / gyro_scale;

        printf("%f,%f,%f,%f,%f,%f\n", ax, ay, az, gx, gy, gz);
    } else {
        ESP_LOGE(TAG, "Failed to read data from MPU6050: %d", ret);
    }
}

void app_main() {
    i2c_master_init();
    mpu6050_init();

    while (1) {
        mpu6050_read_data();
        vTaskDelay(10 / portTICK_PERIOD_MS);  // Sample rate delay
    }
}
