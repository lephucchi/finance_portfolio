"""
Enhanced Sector Mapping for Vietnamese Stock Market
Maps stock symbols to detailed sectors (10+ categories)
"""

# Comprehensive sector mapping for VN market
SECTOR_MAPPING = {
    # BANKING (Ngân hàng)
    'VCB': 'Banking', 'BID': 'Banking', 'CTG': 'Banking', 'ACB': 'Banking',
    'MBB': 'Banking', 'TCB': 'Banking', 'VPB': 'Banking', 'STB': 'Banking',
    'HDB': 'Banking', 'TPB': 'Banking', 'SHB': 'Banking', 'EIB': 'Banking',
    'LPB': 'Banking', 'VIB': 'Banking', 'MSB': 'Banking', 'OCB': 'Banking',
    'BAB': 'Banking', 'ABB': 'Banking', 'PGB': 'Banking', 'NAB': 'Banking',
    'VAB': 'Banking', 'VBB': 'Banking',
    
    # CONSUMER (Hàng tiêu dùng)
    'VNM': 'Consumer', 'SAB': 'Consumer', 'MSN': 'Consumer', 'MWG': 'Consumer',
    'FPT': 'Consumer', 'PNJ': 'Consumer', 'VHC': 'Consumer', 'DGW': 'Consumer',
    'VRE': 'Consumer', 'PLX': 'Consumer', 'MCH': 'Consumer',
    
    # MATERIALS (Vật liệu xây dựng, Thép)
    'HPG': 'Materials', 'HSG': 'Materials', 'NKG': 'Materials', 'HPX': 'Materials',
    'DTL': 'Materials', 'DGC': 'Materials', 'HT1': 'Materials', 'VGC': 'Materials',
    'BMP': 'Materials', 'HRC': 'Materials', 'TVD': 'Materials',
    
    # REAL ESTATE (Bất động sản)
    'VIC': 'Real Estate', 'VHM': 'Real Estate', 'VRE': 'Real Estate', 
    'NLG': 'Real Estate', 'DXG': 'Real Estate', 'PDR': 'Real Estate',
    'DIG': 'Real Estate', 'HDG': 'Real Estate', 'KDH': 'Real Estate',
    'BCM': 'Real Estate', 'NVL': 'Real Estate', 'KBC': 'Real Estate',
    'HDC': 'Real Estate', 'CEO': 'Real Estate', 'SCR': 'Real Estate',
    'HQC': 'Real Estate', 'LDG': 'Real Estate', 'SZC': 'Real Estate',
    
    # TECHNOLOGY (Công nghệ)
    'FPT': 'Technology', 'CMG': 'Technology', 'VGI': 'Technology',
    'ELC': 'Technology', 'ITD': 'Technology', 'SAM': 'Technology',
    'SGT': 'Technology', 'CMT': 'Technology', 'VNT': 'Technology',
    
    # ENERGY (Năng lượng, Điện, Dầu khí)
    'GAS': 'Energy', 'POW': 'Energy', 'PVD': 'Energy', 'PVS': 'Energy',
    'PLX': 'Energy', 'BSR': 'Energy', 'PVT': 'Energy', 'PVG': 'Energy',
    'NT2': 'Energy', 'PC1': 'Energy', 'REE': 'Energy', 'VSH': 'Energy',
    
    # UTILITIES (Điện, Nước, Cơ sở hạ tầng)
    'GEG': 'Utilities', 'BWE': 'Utilities', 'SJD': 'Utilities',
    'VCG': 'Utilities', 'DPM': 'Utilities', 'VSC': 'Utilities',
    
    # HEALTHCARE (Y tế, Dược phẩm)
    'DHG': 'Healthcare', 'DMC': 'Healthcare', 'IMP': 'Healthcare',
    'DCL': 'Healthcare', 'DBD': 'Healthcare', 'TRA': 'Healthcare',
    'PME': 'Healthcare', 'DVN': 'Healthcare',
    
    # FINANCE (Chứng khoán, Bảo hiểm)
    'SSI': 'Finance', 'VCI': 'Finance', 'HCM': 'Finance', 'VND': 'Finance',
    'FTS': 'Finance', 'MBS': 'Finance', 'BSI': 'Finance', 'AGR': 'Finance',
    'BVH': 'Finance', 'BMI': 'Finance', 'PVI': 'Finance', 'PRE': 'Finance',
    
    # TRANSPORTATION (Vận tải, Logistics)
    'GMD': 'Transportation', 'HAH': 'Transportation', 'VJC': 'Transportation',
    'ACV': 'Transportation', 'HVN': 'Transportation', 'VOS': 'Transportation',
    'PVT': 'Transportation', 'TCL': 'Transportation', 'VFC': 'Transportation',
    
    # AGRICULTURE (Nông nghiệp, Thủy sản)
    'VHC': 'Agriculture', 'HNG': 'Agriculture', 'ANV': 'Agriculture',
    'BAF': 'Agriculture', 'AAA': 'Agriculture', 'VNR': 'Agriculture',
    
    # RETAIL (Bán lẻ)
    'MWG': 'Retail', 'FRT': 'Retail', 'DGW': 'Retail', 'PNJ': 'Retail',
    'VGC': 'Retail', 'SBT': 'Retail',
}

# Sector information
SECTOR_INFO = {
    'Banking': {
        'name_vi': 'Ngân hàng',
        'description': 'Ngân hàng thương mại, tài chính',
        'icon': '🏦'
    },
    'Consumer': {
        'name_vi': 'Hàng tiêu dùng',
        'description': 'Hàng tiêu dùng, thực phẩm, đồ uống',
        'icon': '🛒'
    },
    'Materials': {
        'name_vi': 'Vật liệu',
        'description': 'Thép, xi măng, vật liệu xây dựng',
        'icon': '🏗️'
    },
    'Real Estate': {
        'name_vi': 'Bất động sản',
        'description': 'Phát triển bất động sản, khu công nghiệp',
        'icon': '🏠'
    },
    'Technology': {
        'name_vi': 'Công nghệ',
        'description': 'Công nghệ thông tin, viễn thông',
        'icon': '💻'
    },
    'Energy': {
        'name_vi': 'Năng lượng',
        'description': 'Dầu khí, điện lực',
        'icon': '⚡'
    },
    'Utilities': {
        'name_vi': 'Tiện ích',
        'description': 'Điện, nước, cơ sở hạ tầng',
        'icon': '🔌'
    },
    'Healthcare': {
        'name_vi': 'Y tế',
        'description': 'Dược phẩm, thiết bị y tế',
        'icon': '🏥'
    },
    'Finance': {
        'name_vi': 'Tài chính',
        'description': 'Chứng khoán, bảo hiểm',
        'icon': '💰'
    },
    'Transportation': {
        'name_vi': 'Vận tải',
        'description': 'Hàng không, cảng biển, logistics',
        'icon': '✈️'
    },
    'Agriculture': {
        'name_vi': 'Nông nghiệp',
        'description': 'Nông nghiệp, thủy sản',
        'icon': '🌾'
    },
    'Retail': {
        'name_vi': 'Bán lẻ',
        'description': 'Bán lẻ, thương mại điện tử',
        'icon': '🏬'
    },
    'Others': {
        'name_vi': 'Khác',
        'description': 'Các ngành khác',
        'icon': '📊'
    }
}


def get_sector(symbol: str) -> str:
    """Get sector for a stock symbol"""
    return SECTOR_MAPPING.get(symbol, 'Others')


def get_sector_info(sector: str) -> dict:
    """Get sector information"""
    return SECTOR_INFO.get(sector, SECTOR_INFO['Others'])


def get_all_sectors() -> list:
    """Get list of all sectors"""
    return list(SECTOR_INFO.keys())


if __name__ == "__main__":
    print(f"Total sectors: {len(SECTOR_INFO)}")
    print(f"Total mapped symbols: {len(SECTOR_MAPPING)}")
    print("\nSectors:")
    for sector, info in SECTOR_INFO.items():
        count = sum(1 for s in SECTOR_MAPPING.values() if s == sector)
        print(f"  {info['icon']} {sector} ({info['name_vi']}): {count} symbols")
