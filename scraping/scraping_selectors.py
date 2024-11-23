from enum import Enum


class ScrapingSelectorsEnum(Enum):
    PRODUCT_NAME = "div.page-title-container > div.flex-grow-1 > h1"
    SEALED_TOTAL_AVAILABILITY = "#tabContent-info > div > div > div > div.info-list-container > dl > dd:nth-child(3)"
    SINGLES_TOTAL_AVAILABILITY = "#tabContent-info > div > div.col-12.col-lg-6.mx-auto > div > div.info-list-container.col-12.col-md-8.col-lg-12.mx-auto.align-self-start > dl > dd:nth-child(12)"
    TABLE_PRICES = ".article-table .table-body .article-row .col-offer .price-container"
    TABLE_AVAILABILITIES = "div.col-offer.col-auto > div.amount-container.d-none.d-md-flex.justify-content-end.me-3 > span"
    SEALED_IMAGE = "#image > div > img"
    SINGLES_IMAGE = "#image > div > div > div:nth-child(2) > div > img"
    CARD_NUMBER = "#tabContent-info > div > div.col-12.col-lg-6.mx-auto > div > div.info-list-container.col-12.col-md-8.col-lg-12.mx-auto.align-self-start > dl > dd.d-none.d-md-block.col-6.col-xl-7"
    SET_NAME = "#tabContent-info > div > div.col-12.col-lg-6.mx-auto > div > div.info-list-container.col-12.col-md-8.col-lg-12.mx-auto.align-self-start > dl > dd:nth-child(6) > div > a.mb-2"
    POKEMON_SPECIES = "#tabContent-info > div > div.col-12.col-lg-6.mx-auto > div > div.info-list-container.col-12.col-md-8.col-lg-12.mx-auto.align-self-start > dl > dd:nth-child(10) > a"


    # Species and TotalAvailability