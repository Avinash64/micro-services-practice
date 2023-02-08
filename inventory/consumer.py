from main import redis, Product
import time
key = 'order_completed'
group = 'inventory-group'

try:
    redis.xgroup_create(key, group)
except:
    print("Group already exists")

while True:
    try:
        results = redis.xreadgroup(group, key, {key: '>'}, None)

        if results != []:
            for result in results:
                print("r",result)
                obj = result[1][0][1]
                print("obj",obj)
                try:                                                                                                                                                                                                                                    
                    product = Product.get(obj['product_id'])
                    print(product)
                    product.quantity -= int(obj["quantity"])
                    product.save()
                except:
                    redis.xadd('refund_order', obj, '*') 
                    print("refffff")
    except Exception as e:
        print(str(e))
    time.sleep(1)