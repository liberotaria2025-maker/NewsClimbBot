import time

if _name_ == "_main_":
    while True:
        try:
            login(driver)
            buscar_y_retweet(driver)
            driver.quit()
        except Exception as e:
            print("Error:", e)

        # esperar 1 hora
        time.sleep(3600)
