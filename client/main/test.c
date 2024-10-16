#include <stdio.h>
#include <stdlib.h> 
#include <string.h>
#include <time.h>
#include <math.h>
#include "esp_event.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_timer.h"
#include "esp_sleep.h"
#include "esp_heap_caps.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "lwip/err.h"
#include "lwip/sys.h"
#include "nvs_flash.h"
#include "lwip/sockets.h"
#include <inttypes.h> 

static const char* TAG = "WIFI";
////////////////////////////////////////////////////////////////////// PACKETS //////////////////////////////////////////////////////////////////////


void initialize_random(uint64_t time) {
    srand(time);
}

/**
 * Function that generates a random integer based on lower and upper bounds.
 */
int rand_int(int lower_bound, int upper_bound){
    return rand() % (upper_bound - lower_bound + 1) + lower_bound;
}

/**
 * Function that generates a random float based on lower and upper bounds.
 */
float rand_float( float lower_bound, float upper_bound ){
    float scale = (float)rand() / (float)RAND_MAX; 
    return lower_bound + scale * ( upper_bound - lower_bound );      
}
/**
 * Getter for the mac address on an ESP.
 */
void get_mac(uint8_t* baseMac) {
    esp_err_t ret = esp_wifi_get_mac(WIFI_IF_STA, baseMac);
    if (ret == ESP_OK) {
        printf("%02x:%02x:%02x:%02x:%02x:%02x\n",
                    baseMac[0], baseMac[1], baseMac[2],
                    baseMac[3], baseMac[4], baseMac[5]);
    } else {
        printf("Failed to read MAC address");
    }
}


/**
 * Function that gets used to free a certain packet.
 */
void free_packet(char* packet){
    free(packet);
}


/**
 * Function that facilitates the making of a header.
 */
char* create_header(uint16_t* msg_id, uint8_t* protocol_id, uint8_t* transport_layer, uint16_t* msg_length){

    ESP_LOGI(TAG,"antes del malloc");
    ESP_LOGI(TAG, "%lu", esp_get_free_heap_size());

    char* res = (char*) malloc(12);

    if (res == NULL) {
        ESP_LOGI(TAG,"Error de memoria!");  
    }    

    ESP_LOGI(TAG, "%lu", esp_get_free_heap_size());

    ESP_LOGI(TAG,"paso malloc");
    uint8_t baseMac[6];
    ESP_LOGI(TAG,"paso basemac");
    get_mac(baseMac);
    memcpy(res, baseMac, 6);
    memcpy(res + 6, msg_id, 2);
    memcpy(res + 8, protocol_id, 1);
    memcpy(res + 9, transport_layer, 1);
    memcpy(res + 10, msg_length, 2); 

    return res;
}


/**
 * Function that creates a packet based in the protocol_id given.
 */
char* create_packet(uint16_t* msg_id, uint8_t* protocol_id, uint8_t* transport_layer, uint16_t* msg_length){
    uint8_t protocol_packet = *protocol_id;
    char* header = create_header(msg_id, protocol_id, transport_layer, msg_length);
    uint64_t time = esp_timer_get_time();
    initialize_random(time);
    uint8_t batt_level = rand_int(1,100);
    char* packet = NULL;

    if(protocol_packet == 0){
        packet = (char*)malloc(16);

        if (packet == NULL) {
            ESP_LOGI(TAG,"Error de memoria!");
            free_packet(header);
            return NULL;
        }        

        ESP_LOGI(TAG, "%lu", esp_get_free_heap_size());

        memcpy(packet, header, 12);
        free_packet(header);
        memcpy(packet + 12, &time, 4);
    }
    else if(protocol_packet == 1){

        packet = (char*)malloc(17);

        if (packet == NULL) {
            ESP_LOGI(TAG,"Error de memoria!");
            free_packet(header);
            return NULL;
        }

        ESP_LOGI(TAG, "%lu", esp_get_free_heap_size());
        
        memcpy(packet, header, 12);
        free_packet(header);
        memcpy(packet + 12, &time, 4);
        memcpy(packet + 16, &batt_level, 1);
    }
    else if(protocol_packet == 2){
        uint8_t temp = rand_int(5,30);
        uint32_t press = rand_int(1000, 1200); 
        uint8_t hum = rand_int(30, 80);
        float co = rand_float(30.0f, 200.0f);
        ESP_LOGI(TAG,"malloc 2");
        packet = (char*)malloc(27);
        ESP_LOGI(TAG,"salio de malloc 2");

        if (packet == NULL) {
            ESP_LOGI(TAG,"Error de memoria!");
            free_packet(header);
            return NULL;
        }

        ESP_LOGI(TAG, "%lu", esp_get_free_heap_size());

        memcpy(packet, header, 12);
        free_packet(header);
        memcpy(packet + 12, &time, 4);
        memcpy(packet + 16, &batt_level, 1);
        memcpy(packet + 17, &temp, 1);
        memcpy(packet + 18, &press, 4);
        memcpy(packet + 22, &hum, 1);
        memcpy(packet + 23, &co, 4);
    }
    else if(protocol_packet == 3){
        uint8_t temp = rand_int(5,30);
        uint32_t press = rand_int(1000, 1200); 
        uint8_t hum = rand_int(30, 80);
        float co = rand_float(30.0f, 200.0f);
        float amp_x = rand_float(0.0059f, 0.12f);
        float amp_y = rand_float(0.0041f, 0.011f);
        float amp_z = rand_float(0.008f, 0.15f);
        float fre_x = rand_float(29.0f, 31.0f);
        float fre_y = rand_float(59.0f, 61.0f);
        float fre_z = rand_float(89.0f, 91.0f);
        float rms = sqrtf(amp_x*amp_x+amp_y*amp_y+amp_z*amp_z);

        packet = (char*)malloc(55);

        if (packet == NULL) {
            ESP_LOGI(TAG,"Error de memoria!");
            free_packet(header);
            return NULL;
        }

        ESP_LOGI(TAG, "%lu", esp_get_free_heap_size());

        memcpy(packet, header, 12);
        free_packet(header);
        memcpy(packet + 12, &time, 4);
        memcpy(packet + 16, &batt_level, 1);
        memcpy(packet + 17, &temp, 1);
        memcpy(packet + 18, &press, 4);
        memcpy(packet + 22, &hum, 1);
        memcpy(packet + 23, &co, 4);
        memcpy(packet + 27, &amp_x, 4);
        memcpy(packet + 31, &amp_y, 4);
        memcpy(packet + 35, &amp_z, 4);
        memcpy(packet + 39, &fre_x, 4);
        memcpy(packet + 43, &fre_y, 4);
        memcpy(packet + 47, &fre_z, 4);
        memcpy(packet + 51, &rms, 4);
    }
  
    return packet;
}



char* accelerate(){
    char* acc = (char*)malloc(1000);
    for(int i = 0; i<250; i++){
        float random = rand_float(-16.0f, 16.0f);
        memcpy(acc + i*4, &random, 4);
    }

    return acc;
} 

char* gyroscope(){
    char* gyr = (char*)malloc(1000);
    for(int i = 0; i<250; i++){
        float random = rand_float(-1000.0f, 1000.0f);
        memcpy(gyr + i*4, &random, 4);
    }

    return gyr;
} 



////////////////////////////////////////////////////////////////////// WIFI //////////////////////////////////////////////////////////////////////


//Credenciales de WiFi
#define WIFI_SSID  "cc5326"
#define WIFI_PASSWORD "cc532624"
#define SERVER_IP     "10.20.1.1"
#define SERVER_PORT   1236
#define TCP_PORT   1240
#define UDP_PORT   1250


// Variables de WiFi
#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAIL_BIT BIT1
//static const char* TAG = "WIFI";
static int s_retry_num = 0;
static EventGroupHandle_t s_wifi_event_group;


/**
 * WiFi event handler
 *
 * This callback handles WiFi events, such as the start of
 * the connection, disconnection and IP address setup on the
 * network interface.
 *
 * @param arg      Additional information for the callback
 * @param event_base   Event base
 * @param event_id     Event identifier
 * @param event_data   Additional event information
 */
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



/**
 * Initializes Wi-Fi in station mode
 *
 * Initializes Wi-Fi in station mode and connects to a Wi-Fi network
 * with the given SSID and password.
 *
 * @param ssid   SSID of the Wi-Fi network
 * @param password  Password of the Wi-Fi network
 */
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


/**
 * @brief Initialize the Non-Volatile Storage (NVS)
 *
 * The first time NVS is used, the underlying flash storage must be
 * partitioned. This function will erase the storage if it is not already
 * partitioned, and then initialize the NVS.
 */
void nvs_init() {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES ||
        ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
}

// Helper functions
int create_socket(int type) {
    int sock = socket(AF_INET, type, 0);
    if (sock < 0) {
        ESP_LOGE(TAG, "Error creating socket");
    }
    return sock;
}

int connect_to_server(int sock, struct sockaddr_in *server_addr) {
    return connect(sock, (struct sockaddr *)server_addr, sizeof(*server_addr));
}

void send_message(int sock, const char *msg, size_t len) {
    send(sock, msg, len, 0);
}

int receive_message(int sock, char *buffer, size_t buffer_size) {
    int rx_len = recv(sock, buffer, buffer_size - 1, 0);
    if (rx_len >= 0) {
        buffer[rx_len] = '\0';
        ESP_LOGI(TAG, "Received data: %s", buffer);
    } else {
        ESP_LOGE(TAG, "Error receiving data");
    }
    return rx_len;
}


uint16_t get_message_length(uint8_t protocol_id) {
    switch (protocol_id) {
        case 0: return 4;
        case 1: return 5;
        case 2: return 15;
        case 3: return 43;
        case 4: return 48015; 
        default: return 0;
    }
}

void send_packet(int sock, const char *packet, uint16_t msg_length) {
    send(sock, packet, msg_length + 12, 0);
    ESP_LOGI(TAG, "Message sent");
}

void handle_deep_sleep() {
    esp_sleep_enable_timer_wakeup(1000000);
    esp_deep_sleep_start();
}

void ask_config(uint16_t* message_id , uint8_t* transport_layer, uint8_t* protocol_id) {
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr.s_addr);

    int sock = create_socket(SOCK_STREAM);
    if (sock < 0) return ;

    if (connect_to_server(sock, &server_addr) != 0) {
        close(sock);
        return ;
    }

    const char *msg = "Active config pls.#";
    
    uint8_t mac_add[6]; 
    get_mac(mac_add);   

    char mac_str[13]; 
    snprintf(mac_str, sizeof(mac_str), "%02X%02X%02X%02X%02X%02X",
             mac_add[0], mac_add[1], mac_add[2], mac_add[3], mac_add[4], mac_add[5]);

    size_t msg_len = strlen(msg);
    size_t mac_len = strlen(mac_str);
    size_t total_len = msg_len + mac_len;

    char *combined_msg = (char *)malloc(total_len + 1);

    ESP_LOGI(TAG, "%lu", esp_get_free_heap_size());

    if (combined_msg == NULL) {
        ESP_LOGE(TAG, "Memory allocation for packet failed!");
        return;
    }

    memcpy(combined_msg, msg, msg_len);
    memcpy(combined_msg + msg_len, mac_str, mac_len);
    combined_msg[total_len] = '\0';  

    send_message(sock, combined_msg, total_len);

    free(combined_msg);

    char rx_buffer[50];
    int rx_len = receive_message(sock, rx_buffer, sizeof(rx_buffer));
    if (rx_len < 0) {
        close(sock);
        return ;
    }

    ESP_LOGI(TAG, "%c", rx_buffer[0]);
    ESP_LOGI(TAG, "%c", rx_buffer[1]);
    ESP_LOGI(TAG, "%c", rx_buffer[2]);

    char *response = (char*)malloc((rx_len + 1) * sizeof(char));

    if (response == NULL) {
        close(sock);
        return ;
    }

    ESP_LOGI(TAG, "%lu", esp_get_free_heap_size());

    strncpy(response, rx_buffer, rx_len);
    response[rx_len] = '\0';

    close(sock);

    *transport_layer = (uint8_t)(rx_buffer[0] - '0');
    *protocol_id = (uint8_t)(rx_buffer[1] - '0');

    int i = 2;
    while(rx_buffer[i+1] != '#'){
        i++;
    }

    int length = i - 2 + 1;
    char temp[length + 1];
    strncpy(temp, &rx_buffer[2], length); 

    temp[length] = '\0';

    *message_id = (uint16_t)atoi(temp);


    free(response);
}



// Refactored TCP socket function
void socket_tcp(uint16_t msg_id, uint8_t transport_layer, uint8_t protocol_id, uint16_t msg_length) {
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(TCP_PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr.s_addr);

    ESP_LOGI(TAG,"crear socket");
    int sock = create_socket(SOCK_STREAM);
    ESP_LOGI(TAG,"salio de crear socket");

    if (sock < 0) return;

    if (connect_to_server(sock, &server_addr) != 0) {
        close(sock);
        return;
    }

    ESP_LOGI(TAG,"salio de crear socket 2");

    if(protocol_id != 4){
        ESP_LOGI(TAG,"salio de crear socket 3");
        
        char *packet = create_packet(&msg_id, &protocol_id, &transport_layer, &msg_length);
        if(packet == NULL){
            ESP_LOGI(TAG,"Error de packet!");
            return;
        }
        ESP_LOGI(TAG,"salio de crear socket 4");
        send_packet(sock, packet, msg_length);
        free_packet(packet);
    }  
    else{
        int HEADER_SIZE = 12;
        int bytes_sent = 0;
        int CHUNK_SIZE = 1012;
        int remaining_bytes = msg_length;
        uint8_t momentary_protocol_id = 2;

        char *packet = create_packet(&msg_id, &momentary_protocol_id, &transport_layer, &msg_length);

        memcpy(packet + 8, &protocol_id, 1);

        send_packet(sock, packet, 27);
        free_packet(packet);

        char* sending_packet = (char*)malloc(1012);

        char* header = create_header(&msg_id, &protocol_id, &transport_layer, &msg_length);
    
        memcpy(sending_packet, header, HEADER_SIZE);
        
        int j = 0;
        while(j < 24){
            ESP_LOGI(TAG,"j: %u", j);
            uint64_t time = esp_timer_get_time();
            initialize_random(time+j);
            char* acc = accelerate();
            memcpy(sending_packet + 12, acc, CHUNK_SIZE - HEADER_SIZE);
            send_packet(sock, sending_packet, CHUNK_SIZE);
            free_packet(acc);
            j++;
        }
        j = 0;
        while(j < 24){
            ESP_LOGI(TAG,"j: %u", j);
            uint64_t time = esp_timer_get_time();
            initialize_random(time+(j*2));
            char* gyr = gyroscope();
            memcpy(sending_packet + 12, gyr, CHUNK_SIZE - HEADER_SIZE);
            send_packet(sock, packet, CHUNK_SIZE);
            free_packet(gyr);
            j++;
        }

    }

    close(sock);
    handle_deep_sleep();
}

void socket_udp(uint16_t msg_id, uint8_t transport_layer, uint8_t protocol_id, uint16_t msg_length) {
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(UDP_PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr.s_addr);

    int sock = create_socket(SOCK_DGRAM);
    if (sock < 0) return;

    if (protocol_id != 4) {
        while(true){
            socklen_t server_addr_len = sizeof(server_addr); 
            char *packet = create_packet(&msg_id, &protocol_id, &transport_layer, &msg_length);
            sendto(sock, packet, msg_length + 12, 0, (struct sockaddr *)&server_addr, server_addr_len);
            free_packet(packet);

            char rx_buffer[128];
            int rx_len = receive_message(sock, rx_buffer, sizeof(rx_buffer));
            if (rx_len < 0) {
                close(sock);
                return;
            }

            if (strcmp(rx_buffer, "tabien") == 0) break;  
        }  
    } 
    else {
        int HEADER_SIZE = 12;
        int bytes_sent = 0;
        int CHUNK_SIZE = 1012;
        int remaining_bytes = msg_length;
        uint8_t momentary_protocol_id = 2;
        socklen_t server_addr_len = sizeof(server_addr); 

        while(true){
            char *packet = create_packet(&msg_id, &momentary_protocol_id, &transport_layer, &msg_length);

            memcpy(packet + 8, &protocol_id, 1);

            sendto(sock, packet, 27, 0, (struct sockaddr *)&server_addr, server_addr_len);

            free_packet(packet);

            char* sending_packet = (char*)malloc(1012);

            char* header = create_header(&msg_id, &protocol_id, &transport_layer, &msg_length);
        
            memcpy(sending_packet, header, HEADER_SIZE);

            free_packet(header);

            int j = 0;
            while(j < 24){
                ESP_LOGI(TAG,"j: %u", j);
                uint64_t time = esp_timer_get_time();
                initialize_random(time+j);
                char* acc = accelerate();
                memcpy(sending_packet + 12, acc, CHUNK_SIZE - HEADER_SIZE);

                sendto(sock, sending_packet, CHUNK_SIZE, 0, (struct sockaddr *)&server_addr, server_addr_len);
                
                free_packet(acc);
                j++;
            }

            j = 0;
            while(j < 24){
                uint64_t time = esp_timer_get_time();
                initialize_random(time+(j*2));
                char* gyr = gyroscope();
                memcpy(sending_packet + 12, gyr, CHUNK_SIZE - HEADER_SIZE);
            
                sendto(sock, sending_packet, CHUNK_SIZE, 0, (struct sockaddr *)&server_addr, server_addr_len);

            
                free_packet(gyr);
                j++;
            }

            char rx_buffer[128];
            int rx_len = receive_message(sock, rx_buffer, sizeof(rx_buffer));
            if (rx_len < 0) {
                close(sock);
                return;
            }

            if (strcmp(rx_buffer, "tabien") == 0) break; 
        }
    }
    close(sock);
}


////////////////////////////////////////////////////////////////////// MAIN //////////////////////////////////////////////////////////////////////


void app_main(void) {
    bool run = true;
    while (run) {
        nvs_init();
        wifi_init_sta(WIFI_SSID, WIFI_PASSWORD);
        ESP_LOGI(TAG, "Conectado a WiFi!\n"); 

        while (true) {
            uint16_t msg_id = 5;
            uint8_t transport_layer = 5;
            uint8_t protocol_id = 5;

            ESP_LOGI(TAG, "ASKING CONFIG");
            
            ask_config(&msg_id, &transport_layer, &protocol_id);

            uint16_t msg_length = get_message_length(protocol_id);

            ESP_LOGI(TAG, "MSG_ID: %u", msg_id);
            ESP_LOGI(TAG, "TRANSPORT_LAYER: %u", transport_layer);
            ESP_LOGI(TAG, "PROTOCOL_ID: %u", protocol_id);
            ESP_LOGI(TAG, "MESSAGE_LENGTH: %u", msg_length);


            if (transport_layer == 0) {
                socket_tcp(msg_id, transport_layer, protocol_id, msg_length);
                break;
            } else if (transport_layer == 1) {
                socket_udp(msg_id, transport_layer, protocol_id, msg_length);
            }
            else{
                break;
            }
        }
    }
}
