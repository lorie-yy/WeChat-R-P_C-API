# -*- coding: UTF-8 -*-
from rest_framework import serializers
from wechatfans.models import shop_discountinfo



class shop_discountinfoSerializer(serializers.Serializer):
    cloudid = serializers.CharField(read_only=True)
    shopid = serializers.IntegerField(read_only=True)
    discount = serializers.FloatField(read_only=True,default= 0.8)
    totalincome = serializers.IntegerField(read_only=True,default= 0)      #打折
    availablecash = serializers.IntegerField(read_only=True,default= 0)    #打折
    cashed = serializers.IntegerField(read_only=True,default= 0)           #打折

    def create(self, validated_data):
        """
        Create and return a new `shop_discountinfo` instance, given the validated data.
        """
        return shop_discountinfo.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.cloudid = validated_data.get('cloudid', instance.cloudid)
        instance.shopid = validated_data.get('shopid', instance.shopid)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.totalincome = validated_data.get('totalincome', instance.totalincome)
        instance.availablecash = validated_data.get('availablecash', instance.availablecash)
        instance.cashed = validated_data.get('cashed', instance.cashed)
        instance.save()
        return instance

