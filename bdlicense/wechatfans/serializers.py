# -*- coding: UTF-8 -*-
from rest_framework import serializers
from wechatfans.models import shop_discountinfo, ThridPartyConfig, CloudConfig


class shop_discountinfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    cloudid = serializers.CharField(read_only=True)
    shopid = serializers.IntegerField(read_only=True)
    discount = serializers.FloatField(read_only=True,default= 0.8)
    totalincome = serializers.IntegerField(read_only=True,default= 0)      #打折
    availablecash = serializers.IntegerField(read_only=True,default= 0)    #打折
    cashed = serializers.IntegerField(read_only=True,default= 0)           #打折
    username = serializers.CharField(source='cloudtouser.username')
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

class ThridPartyConfigSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    thirdpartname = serializers.CharField()
    url = serializers.CharField()
    type = serializers.CharField()

    def create(self, validated_data):
        """
        Create and return a new `ThridPartyConfig` instance, given the validated data.
        """
        return ThridPartyConfig.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `ThridPartyConfig` instance, given the validated data.
        """
        instance.thirdpartname = validated_data.get('thirdpartname', instance.thirdpartname)
        instance.url = validated_data.get('url', instance.url)
        instance.type = validated_data.get('type', instance.type)
        instance.save()
        return instance

class Shop_discountinfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    cloudid = serializers.CharField()
    shopid = serializers.IntegerField()
    totalincome = serializers.IntegerField()
    availablecash = serializers.IntegerField()
    cashed = serializers.IntegerField()
    discount = serializers.FloatField()

    def create(self, validated_data):
        """
        Create and return a new `shop_discountinfo` instance, given the validated data.
        """
        return shop_discountinfo.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `ThridPartyConfig` instance, given the validated data.
        """
        instance.cloudid = validated_data.get('cloudid', instance.cloudid)
        instance.shopid = validated_data.get('shopid', instance.shopid)
        instance.totalincome = validated_data.get('totalincome', instance.totalincome)
        instance.availablecash = validated_data.get('availablecash', instance.availablecash)
        instance.cashed = validated_data.get('cashed', instance.cashed)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.save()
        return instance

class CloudConfigSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    cloudid = serializers.CharField()
    cloudname = serializers.CharField()
    thirdpart_name = serializers.CharField(source='thirdpart.thirdpartname')


    def create(self, validated_data):
        """
        Create and return a new `CloudConfig` instance, given the validated data.
        """
        return CloudConfig.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `CloudConfig` instance, given the validated data.
        """
        instance.cloudid = validated_data.get('cloudid', instance.cloudid)
        instance.cloudname = validated_data.get('cloudname', instance.cloudname)
        instance.thirdpart = validated_data.get('thirdpart', instance.thirdpart)
        instance.save()
        return instance

class ApplyforWithdrawalRecordsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    paymentmode = serializers.IntegerField()
    shopid = serializers.IntegerField()
    cloudid = serializers.CharField()
    cloudname = serializers.CharField()
    username = serializers.CharField()
    applyfortime = serializers.DateTimeField()
    alipay_name = serializers.CharField()
    alipaynum = serializers.CharField()
    company = serializers.CharField()
    bank_name = serializers.CharField()
    banknum = serializers.CharField()
    getmoney = serializers.IntegerField()
    paymentresult = serializers.IntegerField()
    flag = serializers.IntegerField()
    note = serializers.CharField()


    def create(self, validated_data):
        """
        Create and return a new `CloudConfig` instance, given the validated data.
        """
        return CloudConfig.objects.create(**validated_data)



