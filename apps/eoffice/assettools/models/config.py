from django.db import models
from apps.shared import SimpleAbstractModel

__all__ = ['AssetToolsConfig', 'AssetToolsConfigWarehouse', 'AssetToolsConfigEmployee']


class AssetToolsConfig(SimpleAbstractModel):
    company = models.OneToOneField(
        'company.Company', on_delete=models.CASCADE,
        related_name='asset_tool_company',
    )
    warehouse = models.ManyToManyField(
        'saledata.WareHouse',
        through="AssetToolsConfigWarehouse",
        symmetrical=False,
        blank=True,
        related_name='asset_config_map_warehouse'
    )
    product_type = models.ForeignKey(
        'saledata.ProductType',
        on_delete=models.CASCADE,
        verbose_name='product type of product',
        null=True
    )
    employee_tools_list_access = models.ManyToManyField(
        'hr.Employee',
        through="AssetToolsConfigEmployee",
        symmetrical=False,
        blank=True,
        related_name='asset_config_map_employee'
    )

    class Meta:
        verbose_name = 'Asset tools config'
        verbose_name_plural = 'Asset tools config of company'
        default_permissions = ()
        permissions = ()


class AssetToolsConfigWarehouse(SimpleAbstractModel):
    asset_tools_config = models.ForeignKey(
        'AssetToolsConfig',
        on_delete=models.CASCADE,
        verbose_name='WareHouse of product',
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name='WareHouse of product',
    )

    class Meta:
        verbose_name = 'Asset tools config map warehouse'
        verbose_name_plural = 'Asset tools config map warehouse'
        default_permissions = ()
        permissions = ()


class AssetToolsConfigEmployee(SimpleAbstractModel):
    asset_tools_config = models.ForeignKey(
        'AssetToolsConfig',
        on_delete=models.CASCADE,
        verbose_name='asset tool config',
    )
    employee = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name='Asset tools map employee',
    )

    class Meta:
        verbose_name = 'Asset tools config map warehouse'
        verbose_name_plural = 'Asset tools config map warehouse'
        default_permissions = ()
        permissions = ()
