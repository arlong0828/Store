from django.db import migrations


PRODUCTS = [
    ("Dunk Low", "1600", "commodity_image/0_dunk_low__1600_ORjta4V.jpg"),
    ("Air Jordan Gym Red", "1500", "commodity_image/1_Gym_red___1500_a5FlOTF.jpg"),
    ("Nike Air 270", "1200", "commodity_image/2_Nike_270__1200_ZihNC98.jpg"),
    ("Yeezy", "900", "commodity_image/3_Yeezy_900_UglOihm.jpg"),
    ("NMD", "1300", "commodity_image/4_NMD__1300_U07iqhf.jpg"),
    ("EQT", "2000", "commodity_image/5_EQT_2000_vNZyDpu.jpg"),
    ("Air Force", "2500", "commodity_image/6_Air_force_2500_3AfCGzs.jpg"),
    ("Air Max 95", "1700", "commodity_image/7_Air_max95_1700_bM0kdQs.jpg"),
    ("Converse 1970", "1800", "commodity_image/8_Converse1970_x2gfCrv.jpg"),
    ("Ultra Boost", "1500", "commodity_image/9_Ultra_boost1500_Y8lc1Ox.jpg"),
]


def seed_catalogue(apps, schema_editor):
    Commodity = apps.get_model("store_app", "commodity")
    for name, price, image in PRODUCTS:
        Commodity.objects.get_or_create(
            commodity_Name=name,
            defaults={"commodity_price": price, "commodity_image": image},
        )


def remove_seed_catalogue(apps, schema_editor):
    Commodity = apps.get_model("store_app", "commodity")
    Commodity.objects.filter(commodity_Name__in=[product[0] for product in PRODUCTS]).delete()


class Migration(migrations.Migration):
    dependencies = [("store_app", "0001_initial")]
    operations = [migrations.RunPython(seed_catalogue, remove_seed_catalogue)]
