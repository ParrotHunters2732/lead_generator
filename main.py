from utils import store_business_list


business_list = store_business_list()
if business_list:
    for business in business_list: 
        print()
        print(business)
        print()
