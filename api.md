# Agencies

Types:

```python
from tango.types import Agency, AgencyListResponse
```

Methods:

- <code title="get /api/agencies/{code}/">client.agencies.<a href="./src/tango/resources/agencies.py">retrieve</a>(code) -> <a href="./src/tango/types/agency.py">Agency</a></code>
- <code title="get /api/agencies/">client.agencies.<a href="./src/tango/resources/agencies.py">list</a>(\*\*<a href="src/tango/types/agency_list_params.py">params</a>) -> <a href="./src/tango/types/agency_list_response.py">AgencyListResponse</a></code>

# AssistanceListings

Types:

```python
from tango.types import (
    AssistanceListing,
    AssistanceListingRetrieveResponse,
    AssistanceListingListResponse,
)
```

Methods:

- <code title="get /api/assistance_listings/{number}/">client.assistance_listings.<a href="./src/tango/resources/assistance_listings.py">retrieve</a>(number) -> <a href="./src/tango/types/assistance_listing_retrieve_response.py">AssistanceListingRetrieveResponse</a></code>
- <code title="get /api/assistance_listings/">client.assistance_listings.<a href="./src/tango/resources/assistance_listings.py">list</a>() -> <a href="./src/tango/types/assistance_listing_list_response.py">AssistanceListingListResponse</a></code>

# Bulk

## Entities

Methods:

- <code title="get /api/bulk/entities">client.bulk.entities.<a href="./src/tango/resources/bulk/entities.py">list</a>() -> None</code>

# BusinessTypes

Types:

```python
from tango.types import BusinessType, BusinessTypeListResponse
```

Methods:

- <code title="get /api/business_types/{code}/">client.business_types.<a href="./src/tango/resources/business_types.py">retrieve</a>(code) -> <a href="./src/tango/types/business_type.py">BusinessType</a></code>
- <code title="get /api/business_types/">client.business_types.<a href="./src/tango/resources/business_types.py">list</a>() -> <a href="./src/tango/types/business_type_list_response.py">BusinessTypeListResponse</a></code>

# Contracts

Types:

```python
from tango.types import ContractRetrieveResponse, ContractListResponse
```

Methods:

- <code title="get /api/contracts/{contract_award_unique_key}/">client.contracts.<a href="./src/tango/resources/contracts.py">retrieve</a>(contract_award_unique_key) -> <a href="./src/tango/types/contract_retrieve_response.py">ContractRetrieveResponse</a></code>
- <code title="get /api/contracts/">client.contracts.<a href="./src/tango/resources/contracts.py">list</a>(\*\*<a href="src/tango/types/contract_list_params.py">params</a>) -> <a href="./src/tango/types/contract_list_response.py">ContractListResponse</a></code>

# Departments

Types:

```python
from tango.types import Department, DepartmentListResponse
```

Methods:

- <code title="get /api/departments/{code}/">client.departments.<a href="./src/tango/resources/departments.py">retrieve</a>(code) -> <a href="./src/tango/types/department.py">Department</a></code>
- <code title="get /api/departments/">client.departments.<a href="./src/tango/resources/departments.py">list</a>() -> <a href="./src/tango/types/department_list_response.py">DepartmentListResponse</a></code>

# Entities

Types:

```python
from tango.types import EntityRetrieveResponse, EntityListResponse
```

Methods:

- <code title="get /api/entities/{uei}/">client.entities.<a href="./src/tango/resources/entities.py">retrieve</a>(uei) -> <a href="./src/tango/types/entity_retrieve_response.py">EntityRetrieveResponse</a></code>
- <code title="get /api/entities/">client.entities.<a href="./src/tango/resources/entities.py">list</a>(\*\*<a href="src/tango/types/entity_list_params.py">params</a>) -> <a href="./src/tango/types/entity_list_response.py">EntityListResponse</a></code>

# Idvs

Types:

```python
from tango.types import Idv, IdvListResponse
```

Methods:

- <code title="get /api/idvs/{contract_award_unique_key}/">client.idvs.<a href="./src/tango/resources/idvs/idvs.py">retrieve</a>(contract_award_unique_key) -> <a href="./src/tango/types/idv.py">Idv</a></code>
- <code title="get /api/idvs/">client.idvs.<a href="./src/tango/resources/idvs/idvs.py">list</a>(\*\*<a href="src/tango/types/idv_list_params.py">params</a>) -> <a href="./src/tango/types/idv_list_response.py">IdvListResponse</a></code>

## Awards

Types:

```python
from tango.types.idvs import AwardListResponse
```

Methods:

- <code title="get /api/idvs/{contract_award_unique_key}/awards/">client.idvs.awards.<a href="./src/tango/resources/idvs/awards.py">list</a>(\*, path_contract_award_unique_key, \*\*<a href="src/tango/types/idvs/award_list_params.py">params</a>) -> <a href="./src/tango/types/idvs/award_list_response.py">AwardListResponse</a></code>

# Naics

Types:

```python
from tango.types import NaicsCode, NaicRetrieveResponse, NaicListResponse
```

Methods:

- <code title="get /api/naics/{code}/">client.naics.<a href="./src/tango/resources/naics.py">retrieve</a>(code) -> <a href="./src/tango/types/naic_retrieve_response.py">NaicRetrieveResponse</a></code>
- <code title="get /api/naics/">client.naics.<a href="./src/tango/resources/naics.py">list</a>(\*\*<a href="src/tango/types/naic_list_params.py">params</a>) -> <a href="./src/tango/types/naic_list_response.py">NaicListResponse</a></code>

# Notices

Types:

```python
from tango.types import NoticeRetrieveResponse, NoticeListResponse
```

Methods:

- <code title="get /api/notices/{notice_id}/">client.notices.<a href="./src/tango/resources/notices.py">retrieve</a>(notice_id) -> <a href="./src/tango/types/notice_retrieve_response.py">NoticeRetrieveResponse</a></code>
- <code title="get /api/notices/">client.notices.<a href="./src/tango/resources/notices.py">list</a>(\*\*<a href="src/tango/types/notice_list_params.py">params</a>) -> <a href="./src/tango/types/notice_list_response.py">NoticeListResponse</a></code>

# Offices

Types:

```python
from tango.types import Office, OfficeListResponse
```

Methods:

- <code title="get /api/offices/{code}/">client.offices.<a href="./src/tango/resources/offices.py">retrieve</a>(code) -> <a href="./src/tango/types/office.py">Office</a></code>
- <code title="get /api/offices/">client.offices.<a href="./src/tango/resources/offices.py">list</a>(\*\*<a href="src/tango/types/office_list_params.py">params</a>) -> <a href="./src/tango/types/office_list_response.py">OfficeListResponse</a></code>

# Opportunities

Types:

```python
from tango.types import OpportunityRetrieveResponse, OpportunityListResponse
```

Methods:

- <code title="get /api/opportunities/{opportunity_id}/">client.opportunities.<a href="./src/tango/resources/opportunities.py">retrieve</a>(opportunity_id) -> <a href="./src/tango/types/opportunity_retrieve_response.py">OpportunityRetrieveResponse</a></code>
- <code title="get /api/opportunities/">client.opportunities.<a href="./src/tango/resources/opportunities.py">list</a>(\*\*<a href="src/tango/types/opportunity_list_params.py">params</a>) -> <a href="./src/tango/types/opportunity_list_response.py">OpportunityListResponse</a></code>

# Pscs

Types:

```python
from tango.types import ProductServiceCode, PscListResponse
```

Methods:

- <code title="get /api/psc/{id}/">client.pscs.<a href="./src/tango/resources/pscs.py">retrieve</a>(id) -> <a href="./src/tango/types/product_service_code.py">ProductServiceCode</a></code>
- <code title="get /api/psc/">client.pscs.<a href="./src/tango/resources/pscs.py">list</a>() -> <a href="./src/tango/types/psc_list_response.py">PscListResponse</a></code>

# Schemas

Types:

```python
from tango.types import SchemaRetrieveResponse
```

Methods:

- <code title="get /api/schema/">client.schemas.<a href="./src/tango/resources/schemas.py">retrieve</a>(\*\*<a href="src/tango/types/schema_retrieve_params.py">params</a>) -> <a href="./src/tango/types/schema_retrieve_response.py">SchemaRetrieveResponse</a></code>

# Subawards

Types:

```python
from tango.types import Subaward, SubawardListResponse
```

Methods:

- <code title="get /api/subawards/{id}/">client.subawards.<a href="./src/tango/resources/subawards.py">retrieve</a>(id) -> <a href="./src/tango/types/subaward.py">Subaward</a></code>
- <code title="get /api/subawards/">client.subawards.<a href="./src/tango/resources/subawards.py">list</a>(\*\*<a href="src/tango/types/subaward_list_params.py">params</a>) -> <a href="./src/tango/types/subaward_list_response.py">SubawardListResponse</a></code>

# Versions

Methods:

- <code title="get /api/version/">client.versions.<a href="./src/tango/resources/versions.py">retrieve</a>() -> None</code>
