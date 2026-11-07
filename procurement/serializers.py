from rest_framework import serializers

from .models import (
    PurchaseRequest,
    PurchaseRequestItem,
    RFQ,
    RFQSupplier,
    Quote,
    QuoteItem,
)


class PurchaseRequestItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseRequestItem
        fields = [
            'id',
            'product',
            'quantity',
            'specification',
        ]


class PurchaseRequestSerializer(serializers.ModelSerializer):

    items = PurchaseRequestItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = PurchaseRequest
        fields = [
            'id',
            'organization',
            'requester',
            'request_number',
            'required_date',
            'specification',
            'budget_estimate',
            'priority',
            'department',
            'cost_center',
            'status',
            'items',
            'created_at',
            'updated_at',
        ]


class QuoteItemSerializer(serializers.ModelSerializer):

    estimated_total = serializers.SerializerMethodField()

    class Meta:
        model = QuoteItem
        fields = [
            'id',
            'product',
            'quantity',
            'unit_price',
            'delivery_fee',
            'other_charges',
            'discount',
            'estimated_total',
        ]

    def get_estimated_total(self, obj):
        return obj.estimated_total()


class QuoteSerializer(serializers.ModelSerializer):

    items = QuoteItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Quote
        fields = [
            'id',
            'rfq',
            'supplier',
            'quote_number',
            'valid_until',
            'attachment',
            'notes',
            'status',
            'items',
            'created_at',
            'updated_at',
        ]