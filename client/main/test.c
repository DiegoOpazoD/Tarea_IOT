#include <stdio.h>
#include <stdlib.h> 
#include <string.h>


#include "esp_event.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "lwip/err.h"
#include "lwip/sys.h"
#include "nvs_flash.h"
#include "lwip/sockets.h" // Para sockets

//Credenciales de WiFi

#define WIFI_SSID "SSID"
#define WIFI_PASSWORD "PASSOWRD"
#define SERVER_IP     "192.168.0.1" // IP del servidor
#define SERVER_PORT   1234

// Variables de WiFi
#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAIL_BIT BIT1
static const char* TAG = "WIFI";
static int s_retry_num = 0;
static EventGroupHandle_t s_wifi_event_group;

/**
 * Falta: 
 * - Ver el tema de meoria que me comentó Diego
 * 
 * Aprox: 2 horas.
 */

int rand_int(int lower_bound, int upper_bound){
    int value = rand() % (upper_bound - lower_bound + 1) + lower_bound; 
    return value;
}


float rand_float( float lower_bound, float upper_bound ){
    float scale = rand() / (float) RAND_MAX; 
    return lower_bound + scale * ( upper_bound - lower_bound );      
}


void get_mac(uint8_t* baseMac){
    esp_read_mac(baseMac, ESP_MAC_WIFI_STA);
}


char* create_header(uint16_t* msg_id, uint8_t* protocol_id, uint8_t* transport_layer, uint16_t* msg_length){
    char* res = (char*)malloc(12 * sizeof(char));

    uint8_t baseMac[6];
    get_mac(baseMac);
    memcpy(res, baseMac, 6);
    memcpy(res + 6, msg_id, 2);
    memcpy(res + 8, protocol_id, 1);
    memcpy(res + 9, transport_layer, 1);
    memcpy(res + 10, msg_length, 2); 

    return res;
}


char* create_packet(uint16_t* msg_id, uint8_t* protocol_id, uint8_t* transport_layer, uint16_t* msg_length){
    uint8_t packet = *protocol_id;
    char* header = create_header(msg_id, protocol_id, transport_layer, msg_length);
    uint64_t time = esp_timer_get_time();

    if(packet == 0){
        char* packet = (char*)malloc(16 * sizeof(char));

        memcpy(packet, header, 12);
        free_packet(header);

        memcpy(packet + 12, &time, 4);
    }

    uint8_t batt_level = create_random_int(1,100);

    else if(packet == 1){

        char* packet = (char*)malloc(17 * sizeof(char));

        memcpy(packet, header, 12);
        free_packet(header);

        memcpy(packet + 12, &time, 4);
        memcpy(packet + 16, batt_level, 1);
    }

    else if(packet == 2){
        uint8_t temp = rand_int(5,30);
        uint64_t press = rand_int(1000, 1200); 
        uint8_t hum = rand_int(30, 80);
        float co = rand_float(30.0f, 200.0f);

        char* packet = (char*)malloc(27 * sizeof(char));

        memcpy(packet, header, 12);
        free_packet(header);

        memcpy(packet + 12, &time, 4);
        memcpy(packet + 16, batt_level, 1);
        memcpy(packet + 17, temp, 1);
        memcpy(packet + 18, press, 4);
        memcpy(packet + 22, hum, 1);
        memcpy(packet + 23, co, 4);
    }

    return packet;
}


void free_packet(char* packet){
    free(packet);
}


void event_handler(void* arg, esp_event_base_t event_base,
                          int32_t event_id, void* event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT &&
               event_id == WIFI_EVENT_STA_DISCONNECTED) {
        if (s_retry_num < 10) {
            esp_wifi_connect();
            s_retry_num++;
            ESP_LOGI(TAG, "retry to connect to the AP");
        } else {
            xEventGroupSetBits(s_wifi_event_group, WIFI_FAIL_BIT);
        }
        ESP_LOGI(TAG, "connect to the AP fail");
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*)event_data;
        ESP_LOGI(TAG, "got ip:" IPSTR, IP2STR(&event->ip_info.ip));
        s_retry_num = 0;
        xEventGroupSetBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
    }
}


void wifi_init_sta(char* ssid, char* password) {
    s_wifi_event_group = xEventGroupCreate();

    ESP_ERROR_CHECK(esp_netif_init());

    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    esp_event_handler_instance_t instance_any_id;
    esp_event_handler_instance_t instance_got_ip;
    ESP_ERROR_CHECK(esp_event_handler_instance_register(
        WIFI_EVENT, ESP_EVENT_ANY_ID, &event_handler, NULL, &instance_any_id));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(
        IP_EVENT, IP_EVENT_STA_GOT_IP, &event_handler, NULL, &instance_got_ip));

    wifi_config_t wifi_config;
    memset(&wifi_config, 0, sizeof(wifi_config_t));

    // Set the specific fields
    strcpy((char*)wifi_config.sta.ssid, WIFI_SSID);
    strcpy((char*)wifi_config.sta.password, WIFI_PASSWORD);
    wifi_config.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
    wifi_config.sta.pmf_cfg.capable = true;
    wifi_config.sta.pmf_cfg.required = false;
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "wifi_init_sta finished.");

    EventBits_t bits = xEventGroupWaitBits(s_wifi_event_group,
                                           WIFI_CONNECTED_BIT | WIFI_FAIL_BIT,
                                           pdFALSE, pdFALSE, portMAX_DELAY);

    if (bits & WIFI_CONNECTED_BIT) {
        ESP_LOGI(TAG, "connected to ap SSID:%s password:%s", ssid,
                 password);
    } else if (bits & WIFI_FAIL_BIT) {
        ESP_LOGI(TAG, "Failed to connect to SSID:%s, password:%s", ssid,
                 password);
    } else {
        ESP_LOGE(TAG, "UNEXPECTED EVENT");
    }

    ESP_ERROR_CHECK(esp_event_handler_instance_unregister(
        IP_EVENT, IP_EVENT_STA_GOT_IP, instance_got_ip));
    ESP_ERROR_CHECK(esp_event_handler_instance_unregister(
        WIFI_EVENT, ESP_EVENT_ANY_ID, instance_any_id));
    vEventGroupDelete(s_wifi_event_group);
}


void nvs_init() {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES ||
        ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
}


void socket_tcp(){
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr.s_addr);

    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock < 0) {
        ESP_LOGE(TAG, "Error creating socket");
        return;
    }

    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) != 0) {
        ESP_LOGE(TAG, "Error connecting to the server");
        close(sock);
        return;
    }

    char * msg = "Active config pls.";
    send(sock, msg, strlen(msg), 0);

    char rx_buffer[128];
    int rx_len = recv(sock, rx_buffer, sizeof(rx_buffer) - 1, 0);
    if (rx_len < 0) {
        ESP_LOGE(TAG, "Error receiving data");
        close(sock);
        return;
    }
    rx_buffer[rx_len] = '\0'; 
    ESP_LOGI(TAG, "Received data: %s", rx_buffer);

    // Extract fields from received data
    uint16_t msg_id = *(uint16_t*)(rx_buffer);
    uint8_t protocol_id = *(uint8_t*)(rx_buffer + 2);
    uint8_t transport_layer = 0;
    uint16_t msg_length;

    if (protocol_id == 0) {
        msg_length = 4;
    } else if (protocol_id == 1) {
        msg_length = 5;
    } else if (protocol_id == 2) {
        msg_length = 15;
    }

    char *packet = create_packet(&msg_id, &protocol_id, &transport_layer, &msg_length);
    send(sock, packet, strlen(packet), 0);  

  
    rx_len = recv(sock, rx_buffer, sizeof(rx_buffer) - 1, 0);
    if (rx_len < 0) {
        ESP_LOGE(TAG, "Error receiving data");
        free_packet(packet);  
        close(sock);
        return;
    }
    rx_buffer[rx_len] = '\0'; 
    ESP_LOGI(TAG, "Received data: %s", rx_buffer);

    free_packet(packet);  
    close(sock);    
    esp_deep_sleep(1000000);
}


void app_main(void){
    while (true) {
        nvs_init();
        wifi_init_sta(WIFI_SSID, WIFI_PASSWORD);
        ESP_LOGI(TAG,"Conectado a WiFi!\n"); 
        socket_tcp();
    }
}

