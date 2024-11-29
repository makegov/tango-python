# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["Subaward"]


class Subaward(BaseModel):
    id: int

    prime_award_unique_key: Optional[str] = None

    subaward_action_date: Optional[datetime] = None

    subaward_amount: Optional[float] = None

    subaward_fsrs_report_id: Optional[str] = None

    subaward_number: Optional[str] = None

    subawardee_uei: Optional[str] = None

    prime_award_amount: Optional[float] = None

    prime_award_awarding_agency_code: Optional[str] = None

    prime_award_awarding_agency_name: Optional[str] = None

    prime_award_awarding_department_code: Optional[int] = None

    prime_award_awarding_department_name: Optional[str] = None

    prime_award_awarding_office_code: Optional[str] = None

    prime_award_awarding_office_name: Optional[str] = None

    prime_award_base_action_date: Optional[str] = None

    prime_award_base_action_date_fiscal_year: Optional[int] = None

    prime_award_base_transaction_description: Optional[str] = None

    prime_award_federal_accounts_funding_this_award: Optional[str] = None

    prime_award_funding_agency_code: Optional[str] = None

    prime_award_funding_agency_name: Optional[str] = None

    prime_award_funding_department_code: Optional[int] = None

    prime_award_funding_department_name: Optional[str] = None

    prime_award_funding_office_code: Optional[str] = None

    prime_award_funding_office_name: Optional[str] = None

    prime_award_latest_action_date: Optional[str] = None

    prime_award_latest_action_date_fiscal_year: Optional[int] = None

    prime_award_naics_code: Optional[int] = None

    prime_award_naics_description: Optional[str] = None

    prime_award_object_classes_funding_this_award: Optional[str] = None

    prime_award_parent_piid: Optional[str] = None

    prime_award_piid: Optional[str] = None

    prime_award_program_activities_funding_this_award: Optional[str] = None

    prime_award_project_title: Optional[str] = None

    prime_award_total_outlayed_amount: Optional[float] = None

    prime_award_treasury_accounts_funding_this_award: Optional[str] = None

    prime_awardee_name: Optional[str] = None

    prime_awardee_parent_name: Optional[str] = None

    prime_awardee_parent_uei: Optional[str] = None

    prime_awardee_uei: Optional[str] = None

    subaward_action_date_fiscal_year: Optional[int] = None

    subaward_description: Optional[str] = None

    subaward_fsrs_report_last_modified_date: Optional[str] = None

    subaward_fsrs_report_month: Optional[int] = None

    subaward_fsrs_report_year: Optional[int] = None

    subaward_place_of_performance_cd_current: Optional[str] = None

    subaward_place_of_performance_cd_original: Optional[str] = None

    subaward_primary_place_of_performance_address_zip_code: Optional[str] = None

    subaward_primary_place_of_performance_city_name: Optional[str] = None

    subaward_primary_place_of_performance_country_code: Optional[str] = None

    subaward_primary_place_of_performance_country_name: Optional[str] = None

    subaward_primary_place_of_performance_state_code: Optional[str] = None

    subaward_primary_place_of_performance_state_name: Optional[str] = None

    subaward_recipient_cd_current: Optional[str] = None

    subaward_recipient_cd_original: Optional[str] = None

    subaward_type: Optional[str] = None

    subawardee_address_line_1: Optional[str] = None

    subawardee_business_types: Optional[str] = None

    subawardee_city_name: Optional[str] = None

    subawardee_country_code: Optional[str] = None

    subawardee_country_name: Optional[str] = None

    subawardee_dba_name: Optional[str] = None

    subawardee_duns: Optional[str] = None

    subawardee_foreign_postal_code: Optional[str] = None

    subawardee_highly_compensated_officer_1_amount: Optional[float] = None

    subawardee_highly_compensated_officer_1_name: Optional[str] = None

    subawardee_highly_compensated_officer_2_amount: Optional[float] = None

    subawardee_highly_compensated_officer_2_name: Optional[str] = None

    subawardee_highly_compensated_officer_3_amount: Optional[float] = None

    subawardee_highly_compensated_officer_3_name: Optional[str] = None

    subawardee_highly_compensated_officer_4_amount: Optional[float] = None

    subawardee_highly_compensated_officer_4_name: Optional[str] = None

    subawardee_highly_compensated_officer_5_amount: Optional[float] = None

    subawardee_highly_compensated_officer_5_name: Optional[str] = None

    subawardee_name: Optional[str] = None

    subawardee_parent_duns: Optional[str] = None

    subawardee_parent_name: Optional[str] = None

    subawardee_parent_uei: Optional[str] = None

    subawardee_state_code: Optional[str] = None

    subawardee_state_name: Optional[str] = None

    subawardee_zip_code: Optional[str] = None

    usaspending_permalink: Optional[str] = None
