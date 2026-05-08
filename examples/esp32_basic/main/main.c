/* Minimal odin example for ESP-IDF.
 *
 * The parameter tree is generated from odin.yaml at build time (see
 * odin_generate_c() in the top-level CMakeLists.txt). The generated header
 * exposes `odin_objects` (parameter descriptors), `odin_variables` (backing
 * storage) and `odin_store` (root group). */

#include <stdio.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "odin.h"
#include "odin_core.h"
#include "odin_lookup.h"
#include "odin_security.h"

#include "OD.h"

static void odin_demo_task(void *arg)
{
    (void) arg;

    int32_t  speed   = 0;
    uint16_t voltage = 12000;

    while (1) {
        speed += 10;
        voltage = (uint16_t)(11800 + (speed % 400));

        ODIN_parameter_write(&odin_objects.speed,   &speed,   sizeof(speed),   ODIN_ACCESS_GROUP_INTERNAL);
        ODIN_parameter_write(&odin_objects.voltage, &voltage, sizeof(voltage), ODIN_ACCESS_GROUP_INTERNAL);

        const ODIN_parameter_t *found = ODIN_get_parameter_by_name(&odin_store, "speed", '.');
        int32_t read_back = 0;
        if (found != NULL) {
            ODIN_parameter_read(found, &read_back, sizeof(read_back), ODIN_ACCESS_GROUP_INTERNAL);
        }

        printf("odin: speed=%ld cm/s, voltage=%u mV\n",
               (long) read_back, (unsigned) voltage);

        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void app_main(void)
{
    xTaskCreate(odin_demo_task, "odin_demo", 4096, NULL, 5, NULL);
}
