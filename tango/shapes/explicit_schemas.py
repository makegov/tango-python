"""Explicit schema definitions for all Tango resource types

This module provides comprehensive schema definitions for all resource types
that are independent of the dataclass definitions. These schemas are used by
the SchemaRegistry for validation and type generation.

Schemas are aligned with the API reference at https://tango.makegov.com/api/
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from tango.shapes.schema import FieldSchema

# ============================================================================
# NESTED MODEL SCHEMAS
# ============================================================================

OFFICE_SCHEMA: dict[str, FieldSchema] = {
    "agency": FieldSchema(name="agency", type=str, is_optional=False, is_list=False),
    "code": FieldSchema(name="code", type=str, is_optional=False, is_list=False),
    "name": FieldSchema(name="name", type=str, is_optional=True, is_list=False),
}

# Awards endpoints often return a richer office object (awarding/funding office).
AWARD_OFFICE_SCHEMA: dict[str, FieldSchema] = {
    "office_code": FieldSchema(name="office_code", type=str, is_optional=True, is_list=False),
    "office_name": FieldSchema(name="office_name", type=str, is_optional=True, is_list=False),
    "agency_code": FieldSchema(name="agency_code", type=str, is_optional=True, is_list=False),
    "agency_name": FieldSchema(name="agency_name", type=str, is_optional=True, is_list=False),
    "department_code": FieldSchema(
        name="department_code", type=str, is_optional=True, is_list=False
    ),
    "department_name": FieldSchema(
        name="department_name", type=str, is_optional=True, is_list=False
    ),
}

PERIOD_OF_PERFORMANCE_IDV_SCHEMA: dict[str, FieldSchema] = {
    "start_date": FieldSchema(name="start_date", type=date, is_optional=True, is_list=False),
    "last_date_to_order": FieldSchema(
        name="last_date_to_order", type=date, is_optional=True, is_list=False
    ),
}

OFFICERS_SCHEMA: dict[str, FieldSchema] = {
    "highly_compensated_officer_1_name": FieldSchema(
        name="highly_compensated_officer_1_name", type=str, is_optional=True, is_list=False
    ),
    "highly_compensated_officer_1_amount": FieldSchema(
        name="highly_compensated_officer_1_amount", type=Decimal, is_optional=True, is_list=False
    ),
    "highly_compensated_officer_2_name": FieldSchema(
        name="highly_compensated_officer_2_name", type=str, is_optional=True, is_list=False
    ),
    "highly_compensated_officer_2_amount": FieldSchema(
        name="highly_compensated_officer_2_amount", type=Decimal, is_optional=True, is_list=False
    ),
    "highly_compensated_officer_3_name": FieldSchema(
        name="highly_compensated_officer_3_name", type=str, is_optional=True, is_list=False
    ),
    "highly_compensated_officer_3_amount": FieldSchema(
        name="highly_compensated_officer_3_amount", type=Decimal, is_optional=True, is_list=False
    ),
    "highly_compensated_officer_4_name": FieldSchema(
        name="highly_compensated_officer_4_name", type=str, is_optional=True, is_list=False
    ),
    "highly_compensated_officer_4_amount": FieldSchema(
        name="highly_compensated_officer_4_amount", type=Decimal, is_optional=True, is_list=False
    ),
    "highly_compensated_officer_5_name": FieldSchema(
        name="highly_compensated_officer_5_name", type=str, is_optional=True, is_list=False
    ),
    "highly_compensated_officer_5_amount": FieldSchema(
        name="highly_compensated_officer_5_amount", type=Decimal, is_optional=True, is_list=False
    ),
}


LOCATION_SCHEMA: dict[str, FieldSchema] = {
    "city_name": FieldSchema(name="city_name", type=str, is_optional=True, is_list=False),
    "country_code": FieldSchema(name="country_code", type=str, is_optional=False, is_list=False),
    "country_name": FieldSchema(name="country_name", type=str, is_optional=False, is_list=False),
    "state_code": FieldSchema(name="state_code", type=str, is_optional=True, is_list=False),
    "state_name": FieldSchema(name="state_name", type=str, is_optional=False, is_list=False),
    "zip_code": FieldSchema(name="zip_code", type=str, is_optional=True, is_list=False),
}


PLACE_OF_PERFORMANCE_SCHEMA: dict[str, FieldSchema] = {
    "city_name": FieldSchema(name="city_name", type=str, is_optional=True, is_list=False),
    "state_code": FieldSchema(name="state_code", type=str, is_optional=True, is_list=False),
    "state_name": FieldSchema(name="state_name", type=str, is_optional=False, is_list=False),
    "country_code": FieldSchema(name="country_code", type=str, is_optional=False, is_list=False),
    "country_name": FieldSchema(name="country_name", type=str, is_optional=False, is_list=False),
    "zip_code": FieldSchema(name="zip_code", type=str, is_optional=True, is_list=False),
}


COMPETITION_SCHEMA: dict[str, FieldSchema] = {
    "contract_type": FieldSchema(name="contract_type", type=dict, is_optional=False, is_list=False),
    "extent_competed": FieldSchema(
        name="extent_competed", type=dict, is_optional=False, is_list=False
    ),
    "number_of_offers_received": FieldSchema(
        name="number_of_offers_received", type=int, is_optional=False, is_list=False
    ),
    "other_than_full_and_open_competition": FieldSchema(
        name="other_than_full_and_open_competition", type=dict, is_optional=False, is_list=False
    ),
    "solicitation_date": FieldSchema(
        name="solicitation_date", type=date, is_optional=True, is_list=False
    ),
    "solicitation_identifier": FieldSchema(
        name="solicitation_identifier", type=str, is_optional=True, is_list=False
    ),
    "solicitation_procedures": FieldSchema(
        name="solicitation_procedures", type=dict, is_optional=False, is_list=False
    ),
}


PARENT_AWARD_SCHEMA: dict[str, FieldSchema] = {
    "description": FieldSchema(name="description", type=str, is_optional=True, is_list=False),
    "idv_type": FieldSchema(name="idv_type", type=str, is_optional=True, is_list=False),
    "key": FieldSchema(name="key", type=str, is_optional=False, is_list=False),
    "piid": FieldSchema(name="piid", type=str, is_optional=True, is_list=False),
}


LEGISLATIVE_MANDATES_SCHEMA: dict[str, FieldSchema] = {
    "clinger_cohen_act_planning": FieldSchema(
        name="clinger_cohen_act_planning", type=dict, is_optional=False, is_list=False
    ),
    "construction_wage_rate_requirements": FieldSchema(
        name="construction_wage_rate_requirements", type=dict, is_optional=False, is_list=False
    ),
    "employment_eligibility_verification": FieldSchema(
        name="employment_eligibility_verification", type=dict, is_optional=False, is_list=False
    ),
    "interagency_contracting_authority": FieldSchema(
        name="interagency_contracting_authority", type=dict, is_optional=False, is_list=False
    ),
    "labor_standards": FieldSchema(
        name="labor_standards", type=dict, is_optional=False, is_list=False
    ),
    "materials_supplies_articles_equipment": FieldSchema(
        name="materials_supplies_articles_equipment", type=dict, is_optional=False, is_list=False
    ),
    "other_statutory_authority": FieldSchema(
        name="other_statutory_authority", type=dict, is_optional=False, is_list=False
    ),
    "service_contract_inventory": FieldSchema(
        name="service_contract_inventory", type=dict, is_optional=False, is_list=False
    ),
}


SUBAWARDS_SUMMARY_SCHEMA: dict[str, FieldSchema] = {
    "count": FieldSchema(name="count", type=int, is_optional=False, is_list=False),
    "total_amount": FieldSchema(
        name="total_amount", type=Decimal, is_optional=False, is_list=False
    ),
}


TRANSACTION_SCHEMA: dict[str, FieldSchema] = {
    "action_type": FieldSchema(name="action_type", type=dict, is_optional=False, is_list=False),
    "description": FieldSchema(name="description", type=str, is_optional=False, is_list=False),
    "modification_number": FieldSchema(
        name="modification_number", type=str, is_optional=False, is_list=False
    ),
    "obligated": FieldSchema(name="obligated", type=Decimal, is_optional=False, is_list=False),
    "transaction_date": FieldSchema(
        name="transaction_date", type=date, is_optional=False, is_list=False
    ),
}


DEPARTMENT_SCHEMA: dict[str, FieldSchema] = {
    "abbreviation": FieldSchema(name="abbreviation", type=str, is_optional=True, is_list=False),
    "code": FieldSchema(name="code", type=int, is_optional=True, is_list=False),
    "name": FieldSchema(name="name", type=str, is_optional=False, is_list=False),
}


CONTACT_SCHEMA: dict[str, FieldSchema] = {
    "email": FieldSchema(name="email", type=str, is_optional=True, is_list=False),
    "fax": FieldSchema(name="fax", type=str, is_optional=True, is_list=False),
    "full_name": FieldSchema(name="full_name", type=str, is_optional=True, is_list=False),
    "phone": FieldSchema(name="phone", type=str, is_optional=True, is_list=False),
    "title": FieldSchema(name="title", type=str, is_optional=True, is_list=False),
}


RECIPIENT_PROFILE_SCHEMA: dict[str, FieldSchema] = {
    "uei": FieldSchema(name="uei", type=str, is_optional=True, is_list=False),
    "cage_code": FieldSchema(name="cage_code", type=str, is_optional=True, is_list=False),
    "display_name": FieldSchema(name="display_name", type=str, is_optional=True, is_list=False),
    "legal_business_name": FieldSchema(
        name="legal_business_name", type=str, is_optional=True, is_list=False
    ),
    "parent_uei": FieldSchema(name="parent_uei", type=str, is_optional=True, is_list=False),
    "parent_name": FieldSchema(name="parent_name", type=str, is_optional=True, is_list=False),
    "business_types": FieldSchema(name="business_types", type=str, is_optional=True, is_list=True),
    "location": FieldSchema(
        name="location", type=dict, is_optional=True, is_list=False, nested_model="Location"
    ),
    # Award endpoints may expose these legacy identifiers/fields.
    "cage": FieldSchema(name="cage", type=str, is_optional=True, is_list=False),
    "duns": FieldSchema(name="duns", type=str, is_optional=True, is_list=False),
}


# ============================================================================
# MAIN RESOURCE SCHEMAS
# ============================================================================

CONTRACT_SCHEMA: dict[str, FieldSchema] = {
    "award_date": FieldSchema(name="award_date", type=date, is_optional=True, is_list=False),
    "awarding_office": FieldSchema(
        name="awarding_office", type=dict, is_optional=False, is_list=False, nested_model="Office"
    ),
    "base_and_exercised_options_value": FieldSchema(
        name="base_and_exercised_options_value", type=Decimal, is_optional=True, is_list=False
    ),
    "commercial_item_acquisition_procedures": FieldSchema(
        name="commercial_item_acquisition_procedures", type=dict, is_optional=False, is_list=False
    ),
    "competition": FieldSchema(
        name="competition",
        type=dict,
        is_optional=False,
        is_list=False,
        nested_model="ContractOrIDVCompetition",
    ),
    "consolidated_contract": FieldSchema(
        name="consolidated_contract", type=dict, is_optional=False, is_list=False
    ),
    "contingency_humanitarian_or_peacekeeping_operation": FieldSchema(
        name="contingency_humanitarian_or_peacekeeping_operation",
        type=str,
        is_optional=True,
        is_list=False,
    ),
    "contract_bundling": FieldSchema(
        name="contract_bundling", type=dict, is_optional=False, is_list=False
    ),
    "contract_financing": FieldSchema(
        name="contract_financing", type=str, is_optional=True, is_list=False
    ),
    "cost_accounting_standards_clause": FieldSchema(
        name="cost_accounting_standards_clause", type=dict, is_optional=False, is_list=False
    ),
    "cost_or_pricing_data": FieldSchema(
        name="cost_or_pricing_data", type=str, is_optional=True, is_list=False
    ),
    "description": FieldSchema(name="description", type=str, is_optional=True, is_list=False),
    "dod_acquisition_program": FieldSchema(
        name="dod_acquisition_program", type=str, is_optional=True, is_list=False
    ),
    "dod_transaction_number": FieldSchema(
        name="dod_transaction_number", type=int, is_optional=True, is_list=False
    ),
    "domestic_or_foreign_entity": FieldSchema(
        name="domestic_or_foreign_entity", type=dict, is_optional=False, is_list=False
    ),
    "epa_designated_product": FieldSchema(
        name="epa_designated_product", type=dict, is_optional=False, is_list=False
    ),
    "evaluated_preference": FieldSchema(
        name="evaluated_preference", type=dict, is_optional=False, is_list=False
    ),
    "fair_opportunity_limited_sources": FieldSchema(
        name="fair_opportunity_limited_sources", type=dict, is_optional=False, is_list=False
    ),
    "fed_biz_opps": FieldSchema(name="fed_biz_opps", type=str, is_optional=True, is_list=False),
    "fiscal_year": FieldSchema(name="fiscal_year", type=int, is_optional=False, is_list=False),
    "foreign_funding": FieldSchema(
        name="foreign_funding", type=str, is_optional=True, is_list=False
    ),
    "funding_office": FieldSchema(
        name="funding_office", type=dict, is_optional=False, is_list=False, nested_model="Office"
    ),
    "government_furnished_property": FieldSchema(
        name="government_furnished_property", type=str, is_optional=True, is_list=False
    ),
    "information_technology_commercial_item_category": FieldSchema(
        name="information_technology_commercial_item_category",
        type=dict,
        is_optional=False,
        is_list=False,
    ),
    "inherently_governmental_functions": FieldSchema(
        name="inherently_governmental_functions", type=dict, is_optional=False, is_list=False
    ),
    "key": FieldSchema(name="key", type=str, is_optional=False, is_list=False),
    "legislative_mandates": FieldSchema(
        name="legislative_mandates",
        type=dict,
        is_optional=False,
        is_list=False,
        nested_model="LegislativeMandates",
    ),
    "local_area_set_aside": FieldSchema(
        name="local_area_set_aside", type=str, is_optional=True, is_list=False
    ),
    "major_program": FieldSchema(name="major_program", type=str, is_optional=True, is_list=False),
    "naics_code": FieldSchema(name="naics_code", type=int, is_optional=True, is_list=False),
    "number_of_actions": FieldSchema(
        name="number_of_actions", type=int, is_optional=True, is_list=False
    ),
    "number_of_offers_source": FieldSchema(
        name="number_of_offers_source", type=str, is_optional=True, is_list=False
    ),
    "obligated": FieldSchema(name="obligated", type=Decimal, is_optional=True, is_list=False),
    "parent_award": FieldSchema(
        name="parent_award", type=dict, is_optional=False, is_list=False, nested_model="ParentAward"
    ),
    "performance_based_service_acquisition": FieldSchema(
        name="performance_based_service_acquisition", type=str, is_optional=True, is_list=False
    ),
    "piid": FieldSchema(name="piid", type=str, is_optional=True, is_list=False),
    "place_of_manufacture": FieldSchema(
        name="place_of_manufacture", type=dict, is_optional=False, is_list=False
    ),
    "place_of_performance": FieldSchema(
        name="place_of_performance",
        type=dict,
        is_optional=False,
        is_list=False,
        nested_model="PlaceOfPerformance",
    ),
    "price_evaluation_percent_difference": FieldSchema(
        name="price_evaluation_percent_difference", type=str, is_optional=True, is_list=False
    ),
    "psc_code": FieldSchema(name="psc_code", type=str, is_optional=True, is_list=False),
    "purchase_card_as_payment_method": FieldSchema(
        name="purchase_card_as_payment_method", type=str, is_optional=True, is_list=False
    ),
    "recipient": FieldSchema(
        name="recipient",
        type=dict,
        is_optional=False,
        is_list=False,
        nested_model="RecipientProfile",
    ),
    "recovered_materials_sustainability": FieldSchema(
        name="recovered_materials_sustainability", type=str, is_optional=True, is_list=False
    ),
    "research": FieldSchema(name="research", type=dict, is_optional=False, is_list=False),
    "sam_exception": FieldSchema(name="sam_exception", type=dict, is_optional=False, is_list=False),
    "set_aside": FieldSchema(name="set_aside", type=str, is_optional=False, is_list=False),
    "simplified_procedures_for_certain_commercial_items": FieldSchema(
        name="simplified_procedures_for_certain_commercial_items",
        type=str,
        is_optional=True,
        is_list=False,
    ),
    "small_business_competitiveness_demonstration_program": FieldSchema(
        name="small_business_competitiveness_demonstration_program",
        type=str,
        is_optional=True,
        is_list=False,
    ),
    "solicitation_identifier": FieldSchema(
        name="solicitation_identifier", type=str, is_optional=True, is_list=False
    ),
    "subawards_summary": FieldSchema(
        name="subawards_summary",
        type=dict,
        is_optional=False,
        is_list=False,
        nested_model="SubawardsSummary",
    ),
    "subcontracting_plan": FieldSchema(
        name="subcontracting_plan", type=dict, is_optional=False, is_list=False
    ),
    "total_contract_value": FieldSchema(
        name="total_contract_value", type=Decimal, is_optional=True, is_list=False
    ),
    "tradeoff_process": FieldSchema(
        name="tradeoff_process", type=dict, is_optional=False, is_list=False
    ),
    "transactions": FieldSchema(
        name="transactions",
        type=dict,
        is_optional=False,
        is_list=True,
        nested_model="AwardTransaction",
    ),
    "type_of_set_aside_source": FieldSchema(
        name="type_of_set_aside_source", type=str, is_optional=True, is_list=False
    ),
    "undefinitized_action": FieldSchema(
        name="undefinitized_action", type=str, is_optional=True, is_list=False
    ),
}


ENTITY_SCHEMA: dict[str, FieldSchema] = {
    "business_types": FieldSchema(
        name="business_types", type=dict, is_optional=True, is_list=False
    ),
    "cage_code": FieldSchema(name="cage_code", type=str, is_optional=True, is_list=False),
    "capabilities": FieldSchema(name="capabilities", type=str, is_optional=True, is_list=False),
    "congressional_district": FieldSchema(
        name="congressional_district", type=str, is_optional=True, is_list=False
    ),
    "country_of_incorporation_code": FieldSchema(
        name="country_of_incorporation_code", type=str, is_optional=True, is_list=False
    ),
    "country_of_incorporation_desc": FieldSchema(
        name="country_of_incorporation_desc", type=str, is_optional=True, is_list=False
    ),
    "dba_name": FieldSchema(name="dba_name", type=str, is_optional=True, is_list=False),
    "description": FieldSchema(name="description", type=str, is_optional=True, is_list=False),
    "dodaac": FieldSchema(name="dodaac", type=str, is_optional=True, is_list=False),
    "email_address": FieldSchema(name="email_address", type=str, is_optional=True, is_list=False),
    "entity_division_name": FieldSchema(
        name="entity_division_name", type=str, is_optional=True, is_list=False
    ),
    "entity_division_number": FieldSchema(
        name="entity_division_number", type=str, is_optional=True, is_list=False
    ),
    "entity_start_date": FieldSchema(
        name="entity_start_date", type=str, is_optional=True, is_list=False
    ),
    "entity_structure_code": FieldSchema(
        name="entity_structure_code", type=str, is_optional=True, is_list=False
    ),
    "entity_structure_desc": FieldSchema(
        name="entity_structure_desc", type=str, is_optional=True, is_list=False
    ),
    "entity_type_code": FieldSchema(
        name="entity_type_code", type=str, is_optional=True, is_list=False
    ),
    "entity_type_desc": FieldSchema(
        name="entity_type_desc", type=str, is_optional=True, is_list=False
    ),
    "entity_url": FieldSchema(name="entity_url", type=str, is_optional=True, is_list=False),
    "evs_source": FieldSchema(name="evs_source", type=str, is_optional=True, is_list=False),
    "exclusion_status_flag": FieldSchema(
        name="exclusion_status_flag", type=str, is_optional=True, is_list=False
    ),
    "exclusion_url": FieldSchema(name="exclusion_url", type=str, is_optional=True, is_list=False),
    "federal_obligations": FieldSchema(
        name="federal_obligations", type=dict, is_optional=False, is_list=False
    ),
    "fiscal_year_end_close_date": FieldSchema(
        name="fiscal_year_end_close_date", type=str, is_optional=True, is_list=False
    ),
    "highest_owner": FieldSchema(name="highest_owner", type=dict, is_optional=True, is_list=False),
    "immediate_owner": FieldSchema(
        name="immediate_owner", type=dict, is_optional=True, is_list=False
    ),
    "keywords": FieldSchema(name="keywords", type=str, is_optional=True, is_list=False),
    "last_update_date": FieldSchema(
        name="last_update_date", type=date, is_optional=True, is_list=False
    ),
    "legal_business_name": FieldSchema(
        name="legal_business_name", type=str, is_optional=False, is_list=False
    ),
    "mailing_address": FieldSchema(
        name="mailing_address", type=dict, is_optional=True, is_list=False
    ),
    "naics_codes": FieldSchema(name="naics_codes", type=dict, is_optional=True, is_list=False),
    "organization_structure_code": FieldSchema(
        name="organization_structure_code", type=str, is_optional=True, is_list=False
    ),
    "organization_structure_desc": FieldSchema(
        name="organization_structure_desc", type=str, is_optional=True, is_list=False
    ),
    "physical_address": FieldSchema(
        name="physical_address", type=dict, is_optional=True, is_list=False
    ),
    "primary_naics": FieldSchema(name="primary_naics", type=str, is_optional=True, is_list=False),
    "profit_structure_code": FieldSchema(
        name="profit_structure_code", type=str, is_optional=True, is_list=False
    ),
    "profit_structure_desc": FieldSchema(
        name="profit_structure_desc", type=str, is_optional=True, is_list=False
    ),
    "psc_codes": FieldSchema(name="psc_codes", type=dict, is_optional=True, is_list=False),
    "public_display_flag": FieldSchema(
        name="public_display_flag", type=str, is_optional=True, is_list=False
    ),
    "purpose_of_registration_code": FieldSchema(
        name="purpose_of_registration_code", type=str, is_optional=False, is_list=False
    ),
    "purpose_of_registration_desc": FieldSchema(
        name="purpose_of_registration_desc", type=str, is_optional=False, is_list=False
    ),
    "registered": FieldSchema(name="registered", type=str, is_optional=True, is_list=False),
    "registration_status": FieldSchema(
        name="registration_status", type=str, is_optional=False, is_list=False
    ),
    "relationships": FieldSchema(name="relationships", type=str, is_optional=False, is_list=True),
    "sam_activation_date": FieldSchema(
        name="sam_activation_date", type=date, is_optional=True, is_list=False
    ),
    "sam_expiration_date": FieldSchema(
        name="sam_expiration_date", type=date, is_optional=True, is_list=False
    ),
    "sam_registration_date": FieldSchema(
        name="sam_registration_date", type=date, is_optional=True, is_list=False
    ),
    "sba_business_types": FieldSchema(
        name="sba_business_types", type=dict, is_optional=True, is_list=False
    ),
    "state_of_incorporation_code": FieldSchema(
        name="state_of_incorporation_code", type=str, is_optional=True, is_list=False
    ),
    "state_of_incorporation_desc": FieldSchema(
        name="state_of_incorporation_desc", type=str, is_optional=True, is_list=False
    ),
    "submission_date": FieldSchema(
        name="submission_date", type=date, is_optional=True, is_list=False
    ),
    "uei": FieldSchema(name="uei", type=str, is_optional=False, is_list=False),
    "uei_creation_date": FieldSchema(
        name="uei_creation_date", type=date, is_optional=True, is_list=False
    ),
    "uei_expiration_date": FieldSchema(
        name="uei_expiration_date", type=date, is_optional=True, is_list=False
    ),
    "uei_status": FieldSchema(name="uei_status", type=str, is_optional=True, is_list=False),
}


FORECAST_SCHEMA: dict[str, FieldSchema] = {
    "agency": FieldSchema(name="agency", type=str, is_optional=False, is_list=False),
    "anticipated_award_date": FieldSchema(
        name="anticipated_award_date", type=date, is_optional=True, is_list=False
    ),
    "contract_vehicle": FieldSchema(
        name="contract_vehicle", type=str, is_optional=False, is_list=False
    ),
    "description": FieldSchema(name="description", type=str, is_optional=True, is_list=False),
    "estimated_period": FieldSchema(
        name="estimated_period", type=str, is_optional=False, is_list=False
    ),
    "external_id": FieldSchema(name="external_id", type=str, is_optional=False, is_list=False),
    "fiscal_year": FieldSchema(name="fiscal_year", type=int, is_optional=True, is_list=False),
    "id": FieldSchema(name="id", type=int, is_optional=False, is_list=False),
    "is_active": FieldSchema(name="is_active", type=bool, is_optional=True, is_list=False),
    "naics_code": FieldSchema(name="naics_code", type=str, is_optional=True, is_list=False),
    "place_of_performance": FieldSchema(
        name="place_of_performance", type=str, is_optional=False, is_list=False
    ),
    "primary_contact": FieldSchema(
        name="primary_contact", type=str, is_optional=False, is_list=False
    ),
    "set_aside": FieldSchema(name="set_aside", type=str, is_optional=False, is_list=False),
    "source_system": FieldSchema(name="source_system", type=str, is_optional=False, is_list=False),
    "status": FieldSchema(name="status", type=str, is_optional=True, is_list=False),
    "title": FieldSchema(name="title", type=str, is_optional=False, is_list=False),
}


OPPORTUNITY_SCHEMA: dict[str, FieldSchema] = {
    "active": FieldSchema(name="active", type=bool, is_optional=True, is_list=False),
    "attachments": FieldSchema(
        name="attachments",
        type=dict,
        is_optional=False,
        is_list=True,
        nested_model="OpportunityAttachment",
    ),
    "award_number": FieldSchema(name="award_number", type=str, is_optional=True, is_list=False),
    "description": FieldSchema(name="description", type=str, is_optional=False, is_list=False),
    "first_notice_date": FieldSchema(
        name="first_notice_date", type=datetime, is_optional=False, is_list=False
    ),
    "last_notice_date": FieldSchema(
        name="last_notice_date", type=datetime, is_optional=False, is_list=False
    ),
    "meta": FieldSchema(name="meta", type=dict, is_optional=False, is_list=False),
    "naics_code": FieldSchema(name="naics_code", type=int, is_optional=True, is_list=False),
    "notice_history": FieldSchema(
        name="notice_history",
        type=dict,
        is_optional=False,
        is_list=True,
        nested_model="NoticeHistory",
    ),
    "office": FieldSchema(
        name="office", type=dict, is_optional=False, is_list=False, nested_model="Office"
    ),
    "opportunity_id": FieldSchema(
        name="opportunity_id", type=str, is_optional=False, is_list=False
    ),
    "place_of_performance": FieldSchema(
        name="place_of_performance", type=dict, is_optional=True, is_list=False
    ),
    "primary_contact": FieldSchema(
        name="primary_contact", type=dict, is_optional=True, is_list=False, nested_model="Contact"
    ),
    "psc_code": FieldSchema(name="psc_code", type=str, is_optional=True, is_list=False),
    "response_deadline": FieldSchema(
        name="response_deadline", type=datetime, is_optional=False, is_list=False
    ),
    "sam_url": FieldSchema(name="sam_url", type=str, is_optional=False, is_list=False),
    "set_aside": FieldSchema(name="set_aside", type=dict, is_optional=False, is_list=False),
    "solicitation_number": FieldSchema(
        name="solicitation_number", type=str, is_optional=True, is_list=False
    ),
    "title": FieldSchema(name="title", type=str, is_optional=False, is_list=False),
}


NOTICE_SCHEMA: dict[str, FieldSchema] = {
    "active": FieldSchema(name="active", type=bool, is_optional=False, is_list=False),
    "attachment_count": FieldSchema(
        name="attachment_count", type=int, is_optional=False, is_list=False
    ),
    "award_number": FieldSchema(name="award_number", type=str, is_optional=True, is_list=False),
    "description": FieldSchema(name="description", type=str, is_optional=True, is_list=False),
    "last_updated": FieldSchema(
        name="last_updated", type=datetime, is_optional=False, is_list=False
    ),
    "naics_code": FieldSchema(name="naics_code", type=str, is_optional=True, is_list=False),
    "notice_id": FieldSchema(name="notice_id", type=str, is_optional=False, is_list=False),
    "opportunity": FieldSchema(name="opportunity", type=dict, is_optional=False, is_list=False),
    "posted_date": FieldSchema(name="posted_date", type=datetime, is_optional=False, is_list=False),
    "psc_code": FieldSchema(name="psc_code", type=str, is_optional=False, is_list=False),
    "response_deadline": FieldSchema(
        name="response_deadline", type=datetime, is_optional=False, is_list=False
    ),
    "sam_url": FieldSchema(name="sam_url", type=str, is_optional=False, is_list=False),
    "set_aside": FieldSchema(name="set_aside", type=str, is_optional=True, is_list=False),
    "solicitation_number": FieldSchema(
        name="solicitation_number", type=str, is_optional=True, is_list=False
    ),
    "title": FieldSchema(name="title", type=str, is_optional=False, is_list=False),
}


# Docket-level fields for Protest dockets expansion: dockets(docket_number, filed_date, ...)
PROTEST_DOCKET_SCHEMA: dict[str, FieldSchema] = {
    "source_system": FieldSchema(name="source_system", type=str, is_optional=True, is_list=False),
    "case_number": FieldSchema(name="case_number", type=str, is_optional=True, is_list=False),
    "docket_number": FieldSchema(name="docket_number", type=str, is_optional=True, is_list=False),
    "title": FieldSchema(name="title", type=str, is_optional=True, is_list=False),
    "protester": FieldSchema(name="protester", type=str, is_optional=True, is_list=False),
    "agency": FieldSchema(name="agency", type=str, is_optional=True, is_list=False),
    "solicitation_number": FieldSchema(
        name="solicitation_number", type=str, is_optional=True, is_list=False
    ),
    "case_type": FieldSchema(name="case_type", type=str, is_optional=True, is_list=False),
    "outcome": FieldSchema(name="outcome", type=str, is_optional=True, is_list=False),
    "filed_date": FieldSchema(name="filed_date", type=datetime, is_optional=True, is_list=False),
    "posted_date": FieldSchema(name="posted_date", type=datetime, is_optional=True, is_list=False),
    "decision_date": FieldSchema(
        name="decision_date", type=datetime, is_optional=True, is_list=False
    ),
    "due_date": FieldSchema(name="due_date", type=datetime, is_optional=True, is_list=False),
    "docket_url": FieldSchema(name="docket_url", type=str, is_optional=True, is_list=False),
    "decision_url": FieldSchema(name="decision_url", type=str, is_optional=True, is_list=False),
    "digest": FieldSchema(name="digest", type=str, is_optional=True, is_list=False),
}

PROTEST_SCHEMA: dict[str, FieldSchema] = {
    "case_id": FieldSchema(name="case_id", type=str, is_optional=False, is_list=False),
    "case_number": FieldSchema(name="case_number", type=str, is_optional=True, is_list=False),
    "title": FieldSchema(name="title", type=str, is_optional=True, is_list=False),
    "source_system": FieldSchema(name="source_system", type=str, is_optional=True, is_list=False),
    "outcome": FieldSchema(name="outcome", type=str, is_optional=True, is_list=False),
    "agency": FieldSchema(name="agency", type=str, is_optional=True, is_list=False),
    "protester": FieldSchema(name="protester", type=str, is_optional=True, is_list=False),
    "solicitation_number": FieldSchema(
        name="solicitation_number", type=str, is_optional=True, is_list=False
    ),
    "case_type": FieldSchema(name="case_type", type=str, is_optional=True, is_list=False),
    "filed_date": FieldSchema(name="filed_date", type=datetime, is_optional=True, is_list=False),
    "posted_date": FieldSchema(name="posted_date", type=datetime, is_optional=True, is_list=False),
    "decision_date": FieldSchema(
        name="decision_date", type=datetime, is_optional=True, is_list=False
    ),
    "due_date": FieldSchema(name="due_date", type=datetime, is_optional=True, is_list=False),
    "docket_url": FieldSchema(name="docket_url", type=str, is_optional=True, is_list=False),
    "decision_url": FieldSchema(name="decision_url", type=str, is_optional=True, is_list=False),
    "digest": FieldSchema(name="digest", type=str, is_optional=True, is_list=False),
    "dockets": FieldSchema(
        name="dockets", type=dict, is_optional=True, is_list=True, nested_model="ProtestDocket"
    ),
}


AGENCY_SCHEMA: dict[str, FieldSchema] = {
    "abbreviation": FieldSchema(name="abbreviation", type=str, is_optional=True, is_list=False),
    "code": FieldSchema(name="code", type=str, is_optional=False, is_list=False),
    "department": FieldSchema(name="department", type=int, is_optional=False, is_list=False),
    "name": FieldSchema(name="name", type=str, is_optional=False, is_list=False),
}


# Nested schemas for Grant fields
CFDA_NUMBER_SCHEMA: dict[str, FieldSchema] = {
    "number": FieldSchema(name="number", type=str, is_optional=True, is_list=False),
    "title": FieldSchema(name="title", type=str, is_optional=True, is_list=False),
}

CODE_DESCRIPTION_SCHEMA: dict[str, FieldSchema] = {
    "code": FieldSchema(name="code", type=str, is_optional=True, is_list=False),
    "description": FieldSchema(name="description", type=str, is_optional=True, is_list=False),
}

GRANT_ATTACHMENT_SCHEMA: dict[str, FieldSchema] = {
    "attachment_id": FieldSchema(name="attachment_id", type=str, is_optional=True, is_list=False),
    "mime_type": FieldSchema(name="mime_type", type=str, is_optional=True, is_list=False),
    "name": FieldSchema(name="name", type=str, is_optional=True, is_list=False),
    "posted_date": FieldSchema(name="posted_date", type=datetime, is_optional=True, is_list=False),
    "resource_id": FieldSchema(name="resource_id", type=str, is_optional=True, is_list=False),
    "type": FieldSchema(name="type", type=str, is_optional=True, is_list=False),
    "url": FieldSchema(name="url", type=str, is_optional=True, is_list=False),
}

GRANT_SCHEMA: dict[str, FieldSchema] = {
    "agency_code": FieldSchema(name="agency_code", type=str, is_optional=True, is_list=False),
    "applicant_eligibility_description": FieldSchema(
        name="applicant_eligibility_description", type=str, is_optional=True, is_list=False
    ),
    "description": FieldSchema(name="description", type=str, is_optional=True, is_list=False),
    "funding_activity_category_description": FieldSchema(
        name="funding_activity_category_description", type=str, is_optional=True, is_list=False
    ),
    "grant_id": FieldSchema(name="grant_id", type=int, is_optional=False, is_list=False),
    "grantor_contact": FieldSchema(
        name="grantor_contact", type=dict, is_optional=True, is_list=True
    ),
    "last_updated": FieldSchema(
        name="last_updated", type=datetime, is_optional=True, is_list=False
    ),
    "opportunity_number": FieldSchema(
        name="opportunity_number", type=str, is_optional=False, is_list=False
    ),
    "status": FieldSchema(
        name="status", type=dict, is_optional=True, is_list=False, nested_model="CodeDescription"
    ),
    "title": FieldSchema(name="title", type=str, is_optional=False, is_list=False),
    # Expanded fields
    "cfda_numbers": FieldSchema(
        name="cfda_numbers",
        type=dict,
        is_optional=True,
        is_list=True,
        nested_model="CFDANumber",
    ),
    "applicant_types": FieldSchema(
        name="applicant_types",
        type=dict,
        is_optional=True,
        is_list=True,
        nested_model="CodeDescription",
    ),
    "category": FieldSchema(
        name="category", type=dict, is_optional=True, is_list=False, nested_model="CodeDescription"
    ),
    "funding_categories": FieldSchema(
        name="funding_categories",
        type=dict,
        is_optional=True,
        is_list=True,
        nested_model="CodeDescription",
    ),
    "funding_details": FieldSchema(
        name="funding_details", type=dict, is_optional=True, is_list=True
    ),
    "funding_instruments": FieldSchema(
        name="funding_instruments",
        type=dict,
        is_optional=True,
        is_list=True,
        nested_model="CodeDescription",
    ),
    "important_dates": FieldSchema(
        name="important_dates", type=dict, is_optional=True, is_list=True
    ),
    "attachments": FieldSchema(
        name="attachments",
        type=dict,
        is_optional=True,
        is_list=True,
        nested_model="GrantAttachment",
    ),
}


# ============================================================================
# VEHICLES (Awards) RESOURCE SCHEMAS
# ============================================================================

# Vehicles expose a "competition_details(...)" expansion that shapes an underlying JSON object.
# We model that as a nested schema to allow field selection (including wildcard use).
VEHICLE_COMPETITION_DETAILS_SCHEMA: dict[str, FieldSchema] = {
    "commercial_item_acquisition_procedures": FieldSchema(
        name="commercial_item_acquisition_procedures", type=dict, is_optional=True, is_list=False
    ),
    "evaluated_preference": FieldSchema(
        name="evaluated_preference", type=dict, is_optional=True, is_list=False
    ),
    "extent_competed": FieldSchema(
        name="extent_competed", type=dict, is_optional=True, is_list=False
    ),
    "most_recent_solicitation_date": FieldSchema(
        name="most_recent_solicitation_date", type=date, is_optional=True, is_list=False
    ),
    "number_of_offers_received": FieldSchema(
        name="number_of_offers_received", type=int, is_optional=True, is_list=False
    ),
    "original_solicitation_date": FieldSchema(
        name="original_solicitation_date", type=date, is_optional=True, is_list=False
    ),
    "other_than_full_and_open_competition": FieldSchema(
        name="other_than_full_and_open_competition", type=dict, is_optional=True, is_list=False
    ),
    "set_aside": FieldSchema(name="set_aside", type=dict, is_optional=True, is_list=False),
    "simplified_procedures_for_certain_commercial_items": FieldSchema(
        name="simplified_procedures_for_certain_commercial_items",
        type=dict,
        is_optional=True,
        is_list=False,
    ),
    "small_business_competitiveness_demonstration_program": FieldSchema(
        name="small_business_competitiveness_demonstration_program",
        type=dict,
        is_optional=True,
        is_list=False,
    ),
    "solicitation_identifier": FieldSchema(
        name="solicitation_identifier", type=str, is_optional=True, is_list=False
    ),
    "solicitation_procedures": FieldSchema(
        name="solicitation_procedures", type=dict, is_optional=True, is_list=False
    ),
}


# Vehicles expose a "metrics(...)" expansion bundling computed metrics.
VEHICLE_METRICS_SCHEMA: dict[str, FieldSchema] = {
    "avg_offers_received": FieldSchema(
        name="avg_offers_received", type=float, is_optional=True, is_list=False
    ),
    "award_concentration_hhi": FieldSchema(
        name="award_concentration_hhi", type=float, is_optional=True, is_list=False
    ),
    "order_concentration_hhi": FieldSchema(
        name="order_concentration_hhi", type=float, is_optional=True, is_list=False
    ),
    "competed_rate": FieldSchema(name="competed_rate", type=float, is_optional=True, is_list=False),
    "using_agency_count": FieldSchema(
        name="using_agency_count", type=int, is_optional=True, is_list=False
    ),
    "avg_order_value": FieldSchema(
        name="avg_order_value", type=float, is_optional=True, is_list=False
    ),
    "max_order_value": FieldSchema(
        name="max_order_value", type=float, is_optional=True, is_list=False
    ),
    "top_recipient_share": FieldSchema(
        name="top_recipient_share", type=float, is_optional=True, is_list=False
    ),
    "recent_obligations_24mo": FieldSchema(
        name="recent_obligations_24mo", type=float, is_optional=True, is_list=False
    ),
    "recent_orders_24mo": FieldSchema(
        name="recent_orders_24mo", type=int, is_optional=True, is_list=False
    ),
    "days_since_last_order": FieldSchema(
        name="days_since_last_order", type=int, is_optional=True, is_list=False
    ),
    "obligation_to_ceiling_ratio": FieldSchema(
        name="obligation_to_ceiling_ratio", type=float, is_optional=True, is_list=False
    ),
}


# IDV schema (used for `/api/idvs/`, and also by Vehicles awardees shaping).
IDV_SCHEMA: dict[str, FieldSchema] = {
    # Identifiers
    "uuid": FieldSchema(name="uuid", type=str, is_optional=True, is_list=False),
    "key": FieldSchema(name="key", type=str, is_optional=False, is_list=False),
    "piid": FieldSchema(name="piid", type=str, is_optional=True, is_list=False),
    # Core fields
    "award_date": FieldSchema(name="award_date", type=date, is_optional=True, is_list=False),
    "naics_code": FieldSchema(name="naics_code", type=int, is_optional=True, is_list=False),
    "psc_code": FieldSchema(name="psc_code", type=str, is_optional=True, is_list=False),
    "total_contract_value": FieldSchema(
        name="total_contract_value", type=Decimal, is_optional=True, is_list=False
    ),
    "description": FieldSchema(name="description", type=str, is_optional=True, is_list=False),
    "base_and_exercised_options_value": FieldSchema(
        name="base_and_exercised_options_value", type=Decimal, is_optional=True, is_list=False
    ),
    "fiscal_year": FieldSchema(name="fiscal_year", type=int, is_optional=True, is_list=False),
    "obligated": FieldSchema(name="obligated", type=Decimal, is_optional=True, is_list=False),
    "idv_type": FieldSchema(name="idv_type", type=dict, is_optional=True, is_list=False),
    "multiple_or_single_award_idv": FieldSchema(
        name="multiple_or_single_award_idv", type=dict, is_optional=True, is_list=False
    ),
    "type_of_idc": FieldSchema(name="type_of_idc", type=dict, is_optional=True, is_list=False),
    # Expansions / nested objects
    "recipient": FieldSchema(
        name="recipient",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="RecipientProfile",
    ),
    "place_of_performance": FieldSchema(
        name="place_of_performance",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="PlaceOfPerformance",
    ),
    "officers": FieldSchema(
        name="officers", type=dict, is_optional=True, is_list=False, nested_model="Officers"
    ),
    "parent_award": FieldSchema(
        name="parent_award",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="ParentAward",
    ),
    "awarding_office": FieldSchema(
        name="awarding_office",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="AwardOffice",
    ),
    "funding_office": FieldSchema(
        name="funding_office",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="AwardOffice",
    ),
    "legislative_mandates": FieldSchema(
        name="legislative_mandates",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="LegislativeMandates",
    ),
    "set_aside": FieldSchema(
        name="set_aside", type=dict, is_optional=True, is_list=False, nested_model="CodeDescription"
    ),
    "period_of_performance": FieldSchema(
        name="period_of_performance",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="IDVPeriodOfPerformance",
    ),
    "transactions": FieldSchema(
        name="transactions",
        type=dict,
        is_optional=True,
        is_list=True,
        nested_model="Transaction",
    ),
    "subawards_summary": FieldSchema(
        name="subawards_summary",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="SubawardsSummary",
    ),
    "competition": FieldSchema(
        name="competition",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="ContractOrIDVCompetition",
    ),
    "awards": FieldSchema(
        name="awards", type=dict, is_optional=True, is_list=True, nested_model="Contract"
    ),
    # Alias expansion used in vehicle shaping: orders(...) == IDV child awards/contracts.
    "orders": FieldSchema(
        name="orders", type=dict, is_optional=True, is_list=True, nested_model="Contract"
    ),
    # Shapes that request naics(...) / psc(...)
    "naics": FieldSchema(
        name="naics", type=dict, is_optional=True, is_list=False, nested_model="CodeDescription"
    ),
    "psc": FieldSchema(
        name="psc", type=dict, is_optional=True, is_list=False, nested_model="CodeDescription"
    ),
    # Vehicle membership rollups (present on `/api/vehicles/{uuid}/awardees/`).
    "title": FieldSchema(name="title", type=str, is_optional=True, is_list=False),
    "order_count": FieldSchema(name="order_count", type=int, is_optional=True, is_list=False),
    "idv_obligations": FieldSchema(
        name="idv_obligations", type=Decimal, is_optional=True, is_list=False
    ),
    "idv_contracts_value": FieldSchema(
        name="idv_contracts_value", type=Decimal, is_optional=True, is_list=False
    ),
}


VEHICLE_SCHEMA: dict[str, FieldSchema] = {
    "uuid": FieldSchema(name="uuid", type=str, is_optional=False, is_list=False),
    "solicitation_identifier": FieldSchema(
        name="solicitation_identifier", type=str, is_optional=False, is_list=False
    ),
    "is_synthetic_solicitation": FieldSchema(
        name="is_synthetic_solicitation", type=bool, is_optional=True, is_list=False
    ),
    "agency_id": FieldSchema(name="agency_id", type=str, is_optional=False, is_list=False),
    "organization_id": FieldSchema(
        name="organization_id", type=str, is_optional=True, is_list=False
    ),
    # Live awarding-org snapshot. Returned as a flat dict with keys:
    # `organization_id`, `office_code`, `office_name`, `agency_code`,
    # `agency_name`, `department_code`, `department_name`. Selected as a leaf
    # token (`shape=...,organization`) — not as a sub-selectable expansion.
    "organization": FieldSchema(
        name="organization", type=dict, is_optional=True, is_list=False
    ),
    # Choice fields are returned as {code, description} objects.
    "vehicle_type": FieldSchema(name="vehicle_type", type=dict, is_optional=True, is_list=False),
    "program_acronym": FieldSchema(
        name="program_acronym", type=str, is_optional=True, is_list=False
    ),
    "who_can_use": FieldSchema(name="who_can_use", type=dict, is_optional=True, is_list=False),
    "type_of_idc": FieldSchema(name="type_of_idc", type=dict, is_optional=True, is_list=False),
    "contract_type": FieldSchema(name="contract_type", type=dict, is_optional=True, is_list=False),
    # Deprecated: recomputed from IDVs at request time. Upstream sends `Deprecation: true`.
    "agency_details": FieldSchema(
        name="agency_details", type=dict, is_optional=True, is_list=False
    ),
    "description": FieldSchema(name="description", type=str, is_optional=True, is_list=False),
    "descriptions": FieldSchema(name="descriptions", type=str, is_optional=True, is_list=True),
    "fiscal_year": FieldSchema(name="fiscal_year", type=int, is_optional=True, is_list=False),
    "award_date": FieldSchema(name="award_date", type=date, is_optional=True, is_list=False),
    "latest_award_date": FieldSchema(
        name="latest_award_date", type=date, is_optional=True, is_list=False
    ),
    "last_date_to_order": FieldSchema(
        name="last_date_to_order", type=date, is_optional=True, is_list=False
    ),
    # Denormalized rollups
    "idv_count": FieldSchema(name="idv_count", type=int, is_optional=True, is_list=False),
    "awardee_count": FieldSchema(name="awardee_count", type=int, is_optional=True, is_list=False),
    "order_count": FieldSchema(name="order_count", type=int, is_optional=True, is_list=False),
    "total_obligated": FieldSchema(
        name="total_obligated", type=Decimal, is_optional=True, is_list=False
    ),
    "vehicle_obligations": FieldSchema(
        name="vehicle_obligations", type=Decimal, is_optional=True, is_list=False
    ),
    "vehicle_contracts_value": FieldSchema(
        name="vehicle_contracts_value", type=Decimal, is_optional=True, is_list=False
    ),
    # Opportunity-derived fields (SAM.gov)
    "solicitation_title": FieldSchema(
        name="solicitation_title", type=str, is_optional=True, is_list=False
    ),
    "solicitation_description": FieldSchema(
        name="solicitation_description", type=str, is_optional=True, is_list=False
    ),
    "solicitation_date": FieldSchema(
        name="solicitation_date", type=date, is_optional=True, is_list=False
    ),
    "opportunity_id": FieldSchema(name="opportunity_id", type=str, is_optional=True, is_list=False),
    "naics_code": FieldSchema(name="naics_code", type=int, is_optional=True, is_list=False),
    "psc_code": FieldSchema(name="psc_code", type=str, is_optional=True, is_list=False),
    "set_aside": FieldSchema(name="set_aside", type=str, is_optional=True, is_list=False),
    # Shaping expansions
    "awardees": FieldSchema(
        name="awardees", type=dict, is_optional=True, is_list=True, nested_model="IDV"
    ),
    "metrics": FieldSchema(
        name="metrics",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="VehicleMetrics",
    ),
    # Deprecated expansions (upstream sends `Deprecation: true`).
    "opportunity": FieldSchema(
        name="opportunity", type=dict, is_optional=True, is_list=False, nested_model="Opportunity"
    ),
    "competition_details": FieldSchema(
        name="competition_details",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="VehicleCompetitionDetails",
    ),
}


# Top-level vehicle shape fields that upstream marks deprecated (the API sends
# `Deprecation: true` and recomputes them from IDVs at request time). The client
# emits a `DeprecationWarning` when callers explicitly include these in `shape`.
DEPRECATED_VEHICLE_SHAPE_FIELDS: frozenset[str] = frozenset(
    {"agency_details", "competition_details", "opportunity"}
)


# Organization (agencies hierarchy)
ORGANIZATION_SCHEMA: dict[str, FieldSchema] = {
    "key": FieldSchema(name="key", type=str, is_optional=True, is_list=False),
    "fh_key": FieldSchema(name="fh_key", type=str, is_optional=False, is_list=False),
    "name": FieldSchema(name="name", type=str, is_optional=True, is_list=False),
    "short_name": FieldSchema(name="short_name", type=str, is_optional=True, is_list=False),
    "level": FieldSchema(name="level", type=int, is_optional=True, is_list=False),
    "type": FieldSchema(name="type", type=str, is_optional=True, is_list=False),
}

# OTA (Other Transaction Agreement) - IDV-like
OTA_SCHEMA: dict[str, FieldSchema] = {
    "key": FieldSchema(name="key", type=str, is_optional=False, is_list=False),
    "piid": FieldSchema(name="piid", type=str, is_optional=True, is_list=False),
    "award_date": FieldSchema(name="award_date", type=date, is_optional=True, is_list=False),
    "description": FieldSchema(name="description", type=str, is_optional=True, is_list=False),
    "total_contract_value": FieldSchema(
        name="total_contract_value", type=Decimal, is_optional=True, is_list=False
    ),
    "obligated": FieldSchema(name="obligated", type=Decimal, is_optional=True, is_list=False),
    "recipient": FieldSchema(
        name="recipient",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="RecipientProfile",
    ),
}

# OTIDV (Other Transaction IDV) - IDV-like
OTIDV_SCHEMA: dict[str, FieldSchema] = {
    "key": FieldSchema(name="key", type=str, is_optional=False, is_list=False),
    "piid": FieldSchema(name="piid", type=str, is_optional=True, is_list=False),
    "award_date": FieldSchema(name="award_date", type=date, is_optional=True, is_list=False),
    "description": FieldSchema(name="description", type=str, is_optional=True, is_list=False),
    "total_contract_value": FieldSchema(
        name="total_contract_value", type=Decimal, is_optional=True, is_list=False
    ),
    "obligated": FieldSchema(name="obligated", type=Decimal, is_optional=True, is_list=False),
    "idv_type": FieldSchema(name="idv_type", type=dict, is_optional=True, is_list=False),
    "recipient": FieldSchema(
        name="recipient",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="RecipientProfile",
    ),
}

# Subaward (prime/sub awards)
SUBAWARD_SCHEMA: dict[str, FieldSchema] = {
    "id": FieldSchema(name="id", type=str, is_optional=True, is_list=False),
    "award_key": FieldSchema(name="award_key", type=str, is_optional=True, is_list=False),
    "amount": FieldSchema(name="amount", type=Decimal, is_optional=True, is_list=False),
    "prime_recipient": FieldSchema(
        name="prime_recipient",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="RecipientProfile",
    ),
    "subaward_recipient": FieldSchema(
        name="subaward_recipient",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="RecipientProfile",
    ),
}

# GSA eLibrary Contract
GSA_ELIBRARY_IDV_REF_SCHEMA: dict[str, FieldSchema] = {
    "key": FieldSchema(name="key", type=str, is_optional=True, is_list=False),
    "award_date": FieldSchema(name="award_date", type=date, is_optional=True, is_list=False),
}

GSA_ELIBRARY_CONTRACT_SCHEMA: dict[str, FieldSchema] = {
    "uuid": FieldSchema(name="uuid", type=str, is_optional=False, is_list=False),
    "contract_number": FieldSchema(
        name="contract_number", type=str, is_optional=True, is_list=False
    ),
    "cooperative_purchasing": FieldSchema(
        name="cooperative_purchasing", type=bool, is_optional=True, is_list=False
    ),
    "disaster_recovery_purchasing": FieldSchema(
        name="disaster_recovery_purchasing", type=bool, is_optional=True, is_list=False
    ),
    "file_urls": FieldSchema(name="file_urls", type=list, is_optional=True, is_list=True),
    "schedule": FieldSchema(name="schedule", type=str, is_optional=True, is_list=False),
    "sins": FieldSchema(name="sins", type=list, is_optional=True, is_list=True),
    "idv": FieldSchema(
        name="idv",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="GsaElibraryIdvRef",
    ),
    "recipient": FieldSchema(
        name="recipient",
        type=dict,
        is_optional=True,
        is_list=False,
        nested_model="RecipientProfile",
    ),
}

# IT Dashboard Investment
ITDASHBOARD_INVESTMENT_SCHEMA: dict[str, FieldSchema] = {
    "uii": FieldSchema(name="uii", type=str, is_optional=False, is_list=False),
    "agency_code": FieldSchema(name="agency_code", type=int, is_optional=True, is_list=False),
    "agency_name": FieldSchema(name="agency_name", type=str, is_optional=True, is_list=False),
    "bureau_code": FieldSchema(name="bureau_code", type=int, is_optional=True, is_list=False),
    "bureau_name": FieldSchema(name="bureau_name", type=str, is_optional=True, is_list=False),
    "investment_title": FieldSchema(
        name="investment_title", type=str, is_optional=True, is_list=False
    ),
    "type_of_investment": FieldSchema(
        name="type_of_investment", type=str, is_optional=True, is_list=False
    ),
    "part_of_it_portfolio": FieldSchema(
        name="part_of_it_portfolio", type=str, is_optional=True, is_list=False
    ),
    "updated_time": FieldSchema(
        name="updated_time", type=datetime, is_optional=True, is_list=False
    ),
    "url": FieldSchema(name="url", type=str, is_optional=True, is_list=False),
    "business_case_html": FieldSchema(
        name="business_case_html", type=str, is_optional=True, is_list=False
    ),
    # Expansions: dict (funding/details) and list-of-dict (nested sub-tables).
    # Modeled as opaque dict/list since their inner shapes are dynamic.
    "funding": FieldSchema(name="funding", type=dict, is_optional=True, is_list=False),
    "details": FieldSchema(name="details", type=dict, is_optional=True, is_list=False),
    "cio_evaluation": FieldSchema(name="cio_evaluation", type=list, is_optional=True, is_list=True),
    "contracts": FieldSchema(name="contracts", type=list, is_optional=True, is_list=True),
    "projects": FieldSchema(name="projects", type=list, is_optional=True, is_list=True),
    "cost_pools_towers": FieldSchema(
        name="cost_pools_towers", type=list, is_optional=True, is_list=True
    ),
    "funding_sources": FieldSchema(
        name="funding_sources", type=list, is_optional=True, is_list=True
    ),
    "performance_metrics": FieldSchema(
        name="performance_metrics", type=list, is_optional=True, is_list=True
    ),
    "performance_actual": FieldSchema(
        name="performance_actual", type=list, is_optional=True, is_list=True
    ),
    "operational_analysis": FieldSchema(
        name="operational_analysis", type=list, is_optional=True, is_list=True
    ),
}

# ============================================================================
# SCHEMA REGISTRY MAPPING
# ============================================================================

EXPLICIT_SCHEMAS: dict[str, dict[str, FieldSchema]] = {
    "Office": OFFICE_SCHEMA,
    "AwardOffice": AWARD_OFFICE_SCHEMA,
    "Location": LOCATION_SCHEMA,
    "PlaceOfPerformance": PLACE_OF_PERFORMANCE_SCHEMA,
    "Competition": COMPETITION_SCHEMA,
    "ParentAward": PARENT_AWARD_SCHEMA,
    "LegislativeMandates": LEGISLATIVE_MANDATES_SCHEMA,
    "SubawardsSummary": SUBAWARDS_SUMMARY_SCHEMA,
    "Transaction": TRANSACTION_SCHEMA,
    "Department": DEPARTMENT_SCHEMA,
    "Contact": CONTACT_SCHEMA,
    "RecipientProfile": RECIPIENT_PROFILE_SCHEMA,
    "Contract": CONTRACT_SCHEMA,
    "IDVPeriodOfPerformance": PERIOD_OF_PERFORMANCE_IDV_SCHEMA,
    "Officers": OFFICERS_SCHEMA,
    "Entity": ENTITY_SCHEMA,
    "Forecast": FORECAST_SCHEMA,
    "Opportunity": OPPORTUNITY_SCHEMA,
    "Notice": NOTICE_SCHEMA,
    "Protest": PROTEST_SCHEMA,
    "ProtestDocket": PROTEST_DOCKET_SCHEMA,
    "Agency": AGENCY_SCHEMA,
    "Grant": GRANT_SCHEMA,
    # Vehicles (Awards)
    "Vehicle": VEHICLE_SCHEMA,
    "IDV": IDV_SCHEMA,
    "VehicleCompetitionDetails": VEHICLE_COMPETITION_DETAILS_SCHEMA,
    "VehicleMetrics": VEHICLE_METRICS_SCHEMA,
    # Nested schemas for Grant fields
    "CFDANumber": CFDA_NUMBER_SCHEMA,
    "CodeDescription": CODE_DESCRIPTION_SCHEMA,
    "GrantAttachment": GRANT_ATTACHMENT_SCHEMA,
    # Additional list endpoints
    "Organization": ORGANIZATION_SCHEMA,
    "OTA": OTA_SCHEMA,
    "OTIDV": OTIDV_SCHEMA,
    "Subaward": SUBAWARD_SCHEMA,
    # GSA eLibrary
    "GsaElibraryContract": GSA_ELIBRARY_CONTRACT_SCHEMA,
    "GsaElibraryIdvRef": GSA_ELIBRARY_IDV_REF_SCHEMA,
    # IT Dashboard
    "ITDashboardInvestment": ITDASHBOARD_INVESTMENT_SCHEMA,
}


def get_explicit_schema(model_name: str) -> dict[str, FieldSchema] | None:
    """Get explicit schema for a model by name

    Args:
        model_name: Name of the model (e.g., "Contract", "Entity")

    Returns:
        Dictionary mapping field names to FieldSchema objects, or None if not found

    Examples:
        >>> schema = get_explicit_schema("Contract")
        >>> "key" in schema
        True
        >>> schema["key"].type
        <class 'str'>
    """
    return EXPLICIT_SCHEMAS.get(model_name)


def register_explicit_schemas(schema_registry: Any) -> None:
    """Register all explicit schemas with a SchemaRegistry instance

    This function registers all the explicit schema definitions with the provided
    SchemaRegistry, allowing them to be used for validation and type generation
    without requiring the dataclass models.

    Args:
        schema_registry: SchemaRegistry instance to register schemas with

    Examples:
        >>> from tango.shapes.schema import SchemaRegistry
        >>> registry = SchemaRegistry(auto_register_builtin=False)
        >>> register_explicit_schemas(registry)
        >>> registry.is_registered("Contract")
        True
    """
    for model_name, schema in EXPLICIT_SCHEMAS.items():
        # Store schema directly in the registry's internal dict
        # We use the model name as a string key since we don't have the actual class
        schema_registry._schemas[model_name] = schema
