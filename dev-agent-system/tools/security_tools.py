"""
ADOS Security Tools Implementation
JWT/OAuth2 authentication and vulnerability scanning tools for security crew
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
import json
import os
import hashlib
import secrets
import subprocess
import sys

from pydantic import BaseModel, Field


class AuthSpec(BaseModel):
    """Specification for authentication system generation"""
    auth_type: str = Field(..., description="Type of authentication (jwt, oauth2)")
    issuer: str = Field(..., description="JWT issuer")
    audience: str = Field(..., description="JWT audience")
    secret_key: str = Field(..., description="Secret key for JWT signing")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire: int = Field(default=30, description="Access token expiration in minutes")
    refresh_token_expire: int = Field(default=7, description="Refresh token expiration in days")
    password_hash_method: str = Field(default="bcrypt", description="Password hashing method")


class OAuth2Spec(BaseModel):
    """Specification for OAuth2 implementation"""
    provider: str = Field(..., description="OAuth2 provider (google, github, etc.)")
    client_id: str = Field(..., description="OAuth2 client ID")
    client_secret: str = Field(..., description="OAuth2 client secret")
    redirect_uri: str = Field(..., description="OAuth2 redirect URI")
    scope: List[str] = Field(..., description="OAuth2 scopes")
    auth_url: str = Field(..., description="OAuth2 authorization URL")
    token_url: str = Field(..., description="OAuth2 token URL")
    user_info_url: str = Field(..., description="OAuth2 user info URL")


class VulnerabilitySpec(BaseModel):
    """Specification for vulnerability scanning"""
    scan_type: str = Field(..., description="Type of scan (dependency, code, owasp)")
    target_path: str = Field(..., description="Path to scan")
    severity_threshold: str = Field(default="medium", description="Minimum severity level")
    output_format: str = Field(default="json", description="Output format")
    include_dev_dependencies: bool = Field(default=False, description="Include dev dependencies")


class ThreatModelSpec(BaseModel):
    """Specification for threat modeling"""
    application_type: str = Field(..., description="Type of application (web, api, mobile)")
    components: List[str] = Field(..., description="Application components")
    data_flow: Dict[str, Any] = Field(..., description="Data flow information")
    trust_boundaries: List[str] = Field(..., description="Trust boundaries")
    attack_surfaces: List[str] = Field(..., description="Attack surfaces")


class SecurityTools:
    """Security tools for authentication and vulnerability scanning"""
    
    def __init__(self, project_root: str = ".", logger: Optional[logging.Logger] = None):
        """Initialize security tools"""
        self.project_root = Path(project_root)
        self.logger = logger or logging.getLogger(__name__)
        self.templates_dir = self.project_root / "dev-agent-system" / "crews" / "security" / "kb"
        
    def generate_jwt_auth_system(self, 
                               auth_spec: AuthSpec,
                               output_dir: str = "output/generated_code") -> Dict[str, Any]:
        """Generate JWT authentication system"""
        try:
            self.logger.info(f"Generating JWT auth system with algorithm {auth_spec.algorithm}")
            
            output_path = self.project_root / output_dir / "security" / "auth"
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate JWT handler
            jwt_handler_content = self._generate_jwt_handler(auth_spec)
            (output_path / "jwt_handler.py").write_text(jwt_handler_content)
            
            # Generate auth middleware
            auth_middleware_content = self._generate_auth_middleware(auth_spec)
            (output_path / "auth_middleware.py").write_text(auth_middleware_content)
            
            # Generate password utilities
            password_utils_content = self._generate_password_utils(auth_spec)
            (output_path / "password_utils.py").write_text(password_utils_content)
            
            # Generate auth models
            auth_models_content = self._generate_auth_models()
            (output_path / "auth_models.py").write_text(auth_models_content)
            
            # Generate auth router
            auth_router_content = self._generate_auth_router(auth_spec)
            (output_path / "auth_router.py").write_text(auth_router_content)
            
            # Generate security configuration
            security_config_content = self._generate_security_config(auth_spec)
            (output_path / "security_config.py").write_text(security_config_content)
            
            result = {
                "status": "success",
                "auth_type": auth_spec.auth_type,
                "output_directory": str(output_path),
                "files_generated": [
                    "jwt_handler.py",
                    "auth_middleware.py",
                    "password_utils.py",
                    "auth_models.py",
                    "auth_router.py",
                    "security_config.py"
                ],
                "algorithm": auth_spec.algorithm,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"JWT auth system generated successfully at {output_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate JWT auth system: {e}")
            return {"status": "error", "error": str(e)}
    
    def generate_oauth2_system(self, 
                             oauth2_spec: OAuth2Spec,
                             output_dir: str = "output/generated_code") -> Dict[str, Any]:
        """Generate OAuth2 authentication system"""
        try:
            self.logger.info(f"Generating OAuth2 system for provider {oauth2_spec.provider}")
            
            output_path = self.project_root / output_dir / "security" / "oauth2"
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate OAuth2 client
            oauth2_client_content = self._generate_oauth2_client(oauth2_spec)
            (output_path / "oauth2_client.py").write_text(oauth2_client_content)
            
            # Generate OAuth2 handlers
            oauth2_handlers_content = self._generate_oauth2_handlers(oauth2_spec)
            (output_path / "oauth2_handlers.py").write_text(oauth2_handlers_content)
            
            # Generate OAuth2 models
            oauth2_models_content = self._generate_oauth2_models()
            (output_path / "oauth2_models.py").write_text(oauth2_models_content)
            
            # Generate OAuth2 router
            oauth2_router_content = self._generate_oauth2_router(oauth2_spec)
            (output_path / "oauth2_router.py").write_text(oauth2_router_content)
            
            result = {
                "status": "success",
                "provider": oauth2_spec.provider,
                "output_directory": str(output_path),
                "files_generated": [
                    "oauth2_client.py",
                    "oauth2_handlers.py",
                    "oauth2_models.py",
                    "oauth2_router.py"
                ],
                "scopes": oauth2_spec.scope,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"OAuth2 system generated successfully at {output_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate OAuth2 system: {e}")
            return {"status": "error", "error": str(e)}
    
    def scan_vulnerabilities(self, 
                           vuln_spec: VulnerabilitySpec,
                           output_dir: str = "output/reports") -> Dict[str, Any]:
        """Scan for vulnerabilities using security tools"""
        try:
            self.logger.info(f"Starting {vuln_spec.scan_type} vulnerability scan")
            
            output_path = self.project_root / output_dir / "security"
            output_path.mkdir(parents=True, exist_ok=True)
            
            scan_results = {}
            
            if vuln_spec.scan_type == "dependency":
                scan_results = self._scan_dependencies(vuln_spec, output_path)
            elif vuln_spec.scan_type == "code":
                scan_results = self._scan_code(vuln_spec, output_path)
            elif vuln_spec.scan_type == "owasp":
                scan_results = self._scan_owasp(vuln_spec, output_path)
            else:
                return {"status": "error", "error": f"Unknown scan type: {vuln_spec.scan_type}"}
            
            # Generate vulnerability report
            report_content = self._generate_vulnerability_report(scan_results, vuln_spec)
            report_file = output_path / f"vulnerability_report_{vuln_spec.scan_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.write_text(json.dumps(report_content, indent=2))
            
            result = {
                "status": "success",
                "scan_type": vuln_spec.scan_type,
                "vulnerabilities_found": len(scan_results.get("vulnerabilities", [])),
                "report_file": str(report_file),
                "output_directory": str(output_path),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Vulnerability scan completed: {result['vulnerabilities_found']} issues found")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to scan vulnerabilities: {e}")
            return {"status": "error", "error": str(e)}
    
    def generate_threat_model(self, 
                            threat_spec: ThreatModelSpec,
                            output_dir: str = "output/reports") -> Dict[str, Any]:
        """Generate threat model for application"""
        try:
            self.logger.info(f"Generating threat model for {threat_spec.application_type}")
            
            output_path = self.project_root / output_dir / "security"
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate threat model analysis
            threats = self._analyze_threats(threat_spec)
            mitigations = self._generate_mitigations(threats)
            
            # Generate threat model report
            threat_model = {
                "application_type": threat_spec.application_type,
                "components": threat_spec.components,
                "data_flow": threat_spec.data_flow,
                "trust_boundaries": threat_spec.trust_boundaries,
                "attack_surfaces": threat_spec.attack_surfaces,
                "threats": threats,
                "mitigations": mitigations,
                "generated_at": datetime.now().isoformat()
            }
            
            report_file = output_path / f"threat_model_{threat_spec.application_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.write_text(json.dumps(threat_model, indent=2))
            
            result = {
                "status": "success",
                "application_type": threat_spec.application_type,
                "threats_identified": len(threats),
                "mitigations_suggested": len(mitigations),
                "report_file": str(report_file),
                "output_directory": str(output_path),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Threat model generated: {result['threats_identified']} threats identified")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate threat model: {e}")
            return {"status": "error", "error": str(e)}
    
    def _generate_jwt_handler(self, auth_spec: AuthSpec) -> str:
        """Generate JWT token handler"""
        return f'''"""
JWT Token Handler
Generated by ADOS Security Tools
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class JWTHandler:
    """JWT token handler for authentication"""
    
    def __init__(self):
        self.secret_key = "{auth_spec.secret_key}"
        self.algorithm = "{auth_spec.algorithm}"
        self.access_token_expire = {auth_spec.access_token_expire}
        self.refresh_token_expire = {auth_spec.refresh_token_expire}
        self.issuer = "{auth_spec.issuer}"
        self.audience = "{auth_spec.audience}"
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire)
        to_encode.update({{
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": self.issuer,
            "aud": self.audience,
            "type": "access"
        }})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Access token created for user: {{data.get('sub')}}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create access token: {{e}}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create access token"
            )
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire)
        to_encode.update({{
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": self.issuer,
            "aud": self.audience,
            "type": "refresh"
        }})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Refresh token created for user: {{data.get('sub')}}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create refresh token: {{e}}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create refresh token"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer
            )
            logger.info(f"Token verified for user: {{payload.get('sub')}}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh access token using refresh token"""
        try:
            payload = self.verify_token(refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Create new access token
            new_data = {{
                "sub": payload.get("sub"),
                "email": payload.get("email"),
                "roles": payload.get("roles", [])
            }}
            
            return self.create_access_token(new_data)
        except Exception as e:
            logger.error(f"Failed to refresh access token: {{e}}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not refresh access token"
            )


# Global JWT handler instance
jwt_handler = JWTHandler()
'''
    
    def _generate_auth_middleware(self, auth_spec: AuthSpec) -> str:
        """Generate authentication middleware"""
        return f'''"""
Authentication Middleware
Generated by ADOS Security Tools
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import logging

from .jwt_handler import jwt_handler

logger = logging.getLogger(__name__)
security = HTTPBearer()


class AuthMiddleware:
    """Authentication middleware for FastAPI"""
    
    def __init__(self):
        self.jwt_handler = jwt_handler
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Get current authenticated user"""
        try:
            token = credentials.credentials
            payload = self.jwt_handler.verify_token(token)
            
            # Extract user information from payload
            user_data = {{
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "roles": payload.get("roles", []),
                "permissions": payload.get("permissions", [])
            }}
            
            logger.info(f"User authenticated: {{user_data['user_id']}}")
            return user_data
            
        except Exception as e:
            logger.error(f"Authentication failed: {{e}}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={{"WWW-Authenticate": "Bearer"}}
            )
    
    async def get_current_active_user(self, current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        """Get current active user"""
        # Add additional checks for user status if needed
        if not current_user.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user"
            )
        
        return current_user
    
    def require_roles(self, required_roles: list):
        """Require specific roles for access"""
        def role_checker(current_user: Dict[str, Any] = Depends(self.get_current_user)):
            user_roles = current_user.get("roles", [])
            
            if not any(role in user_roles for role in required_roles):
                logger.warning(f"User {{current_user['user_id']}} lacks required roles: {{required_roles}}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return current_user
        
        return role_checker
    
    def require_permissions(self, required_permissions: list):
        """Require specific permissions for access"""
        def permission_checker(current_user: Dict[str, Any] = Depends(self.get_current_user)):
            user_permissions = current_user.get("permissions", [])
            
            if not any(permission in user_permissions for permission in required_permissions):
                logger.warning(f"User {{current_user['user_id']}} lacks required permissions: {{required_permissions}}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return current_user
        
        return permission_checker


# Global auth middleware instance
auth_middleware = AuthMiddleware()

# Common dependencies
get_current_user = auth_middleware.get_current_user
get_current_active_user = auth_middleware.get_current_active_user
require_roles = auth_middleware.require_roles
require_permissions = auth_middleware.require_permissions
'''
    
    def _generate_password_utils(self, auth_spec: AuthSpec) -> str:
        """Generate password utilities"""
        return f'''"""
Password Utilities
Generated by ADOS Security Tools
"""

from passlib.context import CryptContext
from passlib.hash import bcrypt, argon2
import secrets
import string
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PasswordUtils:
    """Password hashing and verification utilities"""
    
    def __init__(self):
        # Configure password context based on method
        hash_method = "{auth_spec.password_hash_method}"
        
        if hash_method == "bcrypt":
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        elif hash_method == "argon2":
            self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        else:
            # Default to bcrypt
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        try:
            hashed = self.pwd_context.hash(password)
            logger.info("Password hashed successfully")
            return hashed
        except Exception as e:
            logger.error(f"Failed to hash password: {{e}}")
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            is_valid = self.pwd_context.verify(plain_password, hashed_password)
            logger.info(f"Password verification: {{'valid' if is_valid else 'invalid'}}")
            return is_valid
        except Exception as e:
            logger.error(f"Failed to verify password: {{e}}")
            return False
    
    def generate_password(self, length: int = 12) -> str:
        """Generate a secure random password"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(characters) for _ in range(length))
        logger.info(f"Generated password of length {{length}}")
        return password
    
    def check_password_strength(self, password: str) -> dict:
        """Check password strength"""
        strength = {{
            "length": len(password) >= 8,
            "uppercase": any(c.isupper() for c in password),
            "lowercase": any(c.islower() for c in password),
            "digit": any(c.isdigit() for c in password),
            "special": any(c in "!@#$%^&*()_+-=[]{{}}|;:,.<>?" for c in password)
        }}
        
        score = sum(strength.values())
        
        if score < 3:
            level = "weak"
        elif score < 5:
            level = "medium"
        else:
            level = "strong"
        
        return {{
            "score": score,
            "level": level,
            "checks": strength
        }}
    
    def needs_rehash(self, hashed_password: str) -> bool:
        """Check if password needs rehashing"""
        return self.pwd_context.needs_update(hashed_password)


# Global password utils instance
password_utils = PasswordUtils()
'''
    
    def _generate_auth_models(self) -> str:
        """Generate authentication models"""
        return '''"""
Authentication Models
Generated by ADOS Security Tools
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class UserRegister(BaseModel):
    """User registration request model"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: str = Field(..., min_length=2, description="User full name")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""
    refresh_token: str = Field(..., description="Refresh token")


class UserProfile(BaseModel):
    """User profile model"""
    user_id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., description="User full name")
    roles: List[str] = Field(default=[], description="User roles")
    permissions: List[str] = Field(default=[], description="User permissions")
    created_at: datetime = Field(..., description="Account creation date")
    last_login: Optional[datetime] = Field(None, description="Last login date")
    is_active: bool = Field(default=True, description="Account status")


class PasswordChange(BaseModel):
    """Password change request model"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters')
        return v


class PasswordReset(BaseModel):
    """Password reset request model"""
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters')
        return v


class APIResponse(BaseModel):
    """Generic API response model"""
    success: bool = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")
'''
    
    def _generate_auth_router(self, auth_spec: AuthSpec) -> str:
        """Generate authentication router"""
        return f'''"""
Authentication Router
Generated by ADOS Security Tools
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import logging

from .auth_models import *
from .jwt_handler import jwt_handler
from .password_utils import password_utils
from .auth_middleware import get_current_user, get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/login", response_model=TokenResponse)
async def login(user_login: UserLogin) -> TokenResponse:
    """
    User login endpoint
    """
    try:
        # TODO: Implement user authentication logic
        # This is a placeholder - integrate with your user database
        
        # Example user data (replace with actual user lookup)
        user_data = {{
            "sub": "user123",
            "email": user_login.email,
            "roles": ["user"],
            "permissions": ["read"]
        }}
        
        # Create tokens
        access_token = jwt_handler.create_access_token(user_data)
        refresh_token = jwt_handler.create_refresh_token(user_data)
        
        logger.info(f"User logged in: {{user_login.email}}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in={auth_spec.access_token_expire * 60}
        )
        
    except Exception as e:
        logger.error(f"Login failed: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/register", response_model=APIResponse)
async def register(user_register: UserRegister) -> APIResponse:
    """
    User registration endpoint
    """
    try:
        # TODO: Implement user registration logic
        # This is a placeholder - integrate with your user database
        
        # Hash password
        hashed_password = password_utils.hash_password(user_register.password)
        
        # Check password strength
        strength = password_utils.check_password_strength(user_register.password)
        if strength["level"] == "weak":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is too weak"
            )
        
        logger.info(f"User registered: {{user_register.email}}")
        
        return APIResponse(
            success=True,
            message="User registered successfully",
            data={{"user_id": "user123"}}
        )
        
    except Exception as e:
        logger.error(f"Registration failed: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_request: RefreshTokenRequest) -> TokenResponse:
    """
    Refresh access token endpoint
    """
    try:
        access_token = jwt_handler.refresh_access_token(refresh_request.refresh_token)
        
        logger.info("Access token refreshed")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_request.refresh_token,
            token_type="bearer",
            expires_in={auth_spec.access_token_expire * 60}
        )
        
    except Exception as e:
        logger.error(f"Token refresh failed: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> UserProfile:
    """
    Get user profile endpoint
    """
    try:
        # TODO: Implement user profile retrieval
        # This is a placeholder - integrate with your user database
        
        profile = UserProfile(
            user_id=current_user["user_id"],
            email=current_user["email"],
            full_name="User Name",
            roles=current_user.get("roles", []),
            permissions=current_user.get("permissions", []),
            created_at=datetime.now(),
            last_login=datetime.now(),
            is_active=True
        )
        
        logger.info(f"Profile retrieved for user: {{current_user['user_id']}}")
        return profile
        
    except Exception as e:
        logger.error(f"Profile retrieval failed: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve profile"
        )


@router.post("/change-password", response_model=APIResponse)
async def change_password(
    password_change: PasswordChange,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> APIResponse:
    """
    Change user password endpoint
    """
    try:
        # TODO: Implement password change logic
        # This is a placeholder - integrate with your user database
        
        # Check password strength
        strength = password_utils.check_password_strength(password_change.new_password)
        if strength["level"] == "weak":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password is too weak"
            )
        
        # Hash new password
        hashed_password = password_utils.hash_password(password_change.new_password)
        
        logger.info(f"Password changed for user: {{current_user['user_id']}}")
        
        return APIResponse(
            success=True,
            message="Password changed successfully"
        )
        
    except Exception as e:
        logger.error(f"Password change failed: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not change password"
        )


@router.post("/logout", response_model=APIResponse)
async def logout(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> APIResponse:
    """
    User logout endpoint
    """
    try:
        # TODO: Implement token blacklisting if needed
        # This is a placeholder for logout logic
        
        logger.info(f"User logged out: {{current_user['user_id']}}")
        
        return APIResponse(
            success=True,
            message="Logged out successfully"
        )
        
    except Exception as e:
        logger.error(f"Logout failed: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not logout"
        )
'''
    
    def _generate_security_config(self, auth_spec: AuthSpec) -> str:
        """Generate security configuration"""
        return f'''"""
Security Configuration
Generated by ADOS Security Tools
"""

import os
from typing import Dict, Any
from pydantic import BaseSettings


class SecurityConfig(BaseSettings):
    """Security configuration settings"""
    
    # JWT Settings
    JWT_SECRET_KEY: str = "{auth_spec.secret_key}"
    JWT_ALGORITHM: str = "{auth_spec.algorithm}"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = {auth_spec.access_token_expire}
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = {auth_spec.refresh_token_expire}
    JWT_ISSUER: str = "{auth_spec.issuer}"
    JWT_AUDIENCE: str = "{auth_spec.audience}"
    
    # Password Settings
    PASSWORD_HASH_METHOD: str = "{auth_spec.password_hash_method}"
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # Security Headers
    CORS_ORIGINS: list = ["http://localhost:3000"]
    CORS_METHODS: list = ["GET", "POST", "PUT", "DELETE"]
    CORS_HEADERS: list = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Session Settings
    SESSION_COOKIE_NAME: str = "session"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "strict"
    
    # CSRF Protection
    CSRF_PROTECTION_ENABLED: bool = True
    CSRF_TOKEN_HEADER: str = "X-CSRF-Token"
    
    # Additional Security
    FORCE_HTTPS: bool = True
    HSTS_MAX_AGE: int = 31536000  # 1 year
    CONTENT_TYPE_OPTIONS: str = "nosniff"
    FRAME_OPTIONS: str = "DENY"
    XSS_PROTECTION: str = "1; mode=block"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global security configuration
security_config = SecurityConfig()


def get_security_headers() -> Dict[str, str]:
    """Get security headers for responses"""
    headers = {{}}
    
    if security_config.FORCE_HTTPS:
        headers["Strict-Transport-Security"] = f"max-age={{security_config.HSTS_MAX_AGE}}; includeSubDomains"
    
    headers["X-Content-Type-Options"] = security_config.CONTENT_TYPE_OPTIONS
    headers["X-Frame-Options"] = security_config.FRAME_OPTIONS
    headers["X-XSS-Protection"] = security_config.XSS_PROTECTION
    
    return headers


def get_cors_settings() -> Dict[str, Any]:
    """Get CORS configuration"""
    return {{
        "allow_origins": security_config.CORS_ORIGINS,
        "allow_methods": security_config.CORS_METHODS,
        "allow_headers": security_config.CORS_HEADERS,
        "allow_credentials": True
    }}
'''
    
    def _generate_oauth2_client(self, oauth2_spec: OAuth2Spec) -> str:
        """Generate OAuth2 client"""
        return f'''"""
OAuth2 Client
Generated by ADOS Security Tools
"""

import httpx
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)


class OAuth2Client:
    """OAuth2 client for {oauth2_spec.provider}"""
    
    def __init__(self):
        self.provider = "{oauth2_spec.provider}"
        self.client_id = "{oauth2_spec.client_id}"
        self.client_secret = "{oauth2_spec.client_secret}"
        self.redirect_uri = "{oauth2_spec.redirect_uri}"
        self.scope = {oauth2_spec.scope}
        self.auth_url = "{oauth2_spec.auth_url}"
        self.token_url = "{oauth2_spec.token_url}"
        self.user_info_url = "{oauth2_spec.user_info_url}"
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Get OAuth2 authorization URL"""
        params = {{
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scope),
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent"
        }}
        
        if state:
            params["state"] = state
        
        url = f"{{self.auth_url}}?{{urlencode(params)}}"
        logger.info(f"Generated authorization URL for {{self.provider}}")
        return url
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        try:
            data = {{
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri
            }}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers={{"Accept": "application/json"}}
                )
                response.raise_for_status()
                
                tokens = response.json()
                logger.info(f"Successfully exchanged code for tokens with {{self.provider}}")
                return tokens
                
        except Exception as e:
            logger.error(f"Failed to exchange code for tokens: {{e}}")
            raise
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            data = {{
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers={{"Accept": "application/json"}}
                )
                response.raise_for_status()
                
                tokens = response.json()
                logger.info(f"Successfully refreshed access token with {{self.provider}}")
                return tokens
                
        except Exception as e:
            logger.error(f"Failed to refresh access token: {{e}}")
            raise
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth2 provider"""
        try:
            headers = {{
                "Authorization": f"Bearer {{access_token}}",
                "Accept": "application/json"
            }}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.user_info_url,
                    headers=headers
                )
                response.raise_for_status()
                
                user_info = response.json()
                logger.info(f"Successfully retrieved user info from {{self.provider}}")
                return user_info
                
        except Exception as e:
            logger.error(f"Failed to get user info: {{e}}")
            raise
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke OAuth2 token"""
        try:
            # Implementation depends on OAuth2 provider
            # This is a placeholder for token revocation
            logger.info(f"Token revoked for {{self.provider}}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke token: {{e}}")
            return False


# Global OAuth2 client instance
oauth2_client = OAuth2Client()
'''
    
    def _generate_oauth2_handlers(self, oauth2_spec: OAuth2Spec) -> str:
        """Generate OAuth2 handlers"""
        return f'''"""
OAuth2 Handlers
Generated by ADOS Security Tools
"""

from typing import Dict, Any, Optional
import secrets
import logging
from fastapi import HTTPException, status

from .oauth2_client import oauth2_client

logger = logging.getLogger(__name__)


class OAuth2Handler:
    """OAuth2 authentication handler"""
    
    def __init__(self):
        self.client = oauth2_client
        self.pending_states = {{}}  # In production, use Redis or database
    
    def initiate_oauth2_flow(self) -> Dict[str, str]:
        """Initiate OAuth2 authentication flow"""
        try:
            # Generate state for CSRF protection
            state = secrets.token_urlsafe(32)
            self.pending_states[state] = {{"timestamp": datetime.now()}}
            
            # Get authorization URL
            auth_url = self.client.get_authorization_url(state)
            
            logger.info(f"OAuth2 flow initiated for {{self.client.provider}}")
            
            return {{
                "authorization_url": auth_url,
                "state": state
            }}
            
        except Exception as e:
            logger.error(f"Failed to initiate OAuth2 flow: {{e}}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not initiate OAuth2 flow"
            )
    
    async def handle_oauth2_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Handle OAuth2 callback"""
        try:
            # Verify state for CSRF protection
            if state not in self.pending_states:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state parameter"
                )
            
            # Remove state from pending
            del self.pending_states[state]
            
            # Exchange code for tokens
            tokens = await self.client.exchange_code_for_tokens(code)
            
            # Get user information
            user_info = await self.client.get_user_info(tokens["access_token"])
            
            # TODO: Create or update user in database
            # This is a placeholder - integrate with your user system
            
            logger.info(f"OAuth2 callback processed for {{self.client.provider}}")
            
            return {{
                "tokens": tokens,
                "user_info": user_info
            }}
            
        except Exception as e:
            logger.error(f"Failed to handle OAuth2 callback: {{e}}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OAuth2 callback failed"
            )
    
    async def refresh_oauth2_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh OAuth2 access token"""
        try:
            tokens = await self.client.refresh_access_token(refresh_token)
            
            logger.info(f"OAuth2 token refreshed for {{self.client.provider}}")
            
            return tokens
            
        except Exception as e:
            logger.error(f"Failed to refresh OAuth2 token: {{e}}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not refresh OAuth2 token"
            )
    
    async def revoke_oauth2_token(self, token: str) -> bool:
        """Revoke OAuth2 token"""
        try:
            result = await self.client.revoke_token(token)
            
            if result:
                logger.info(f"OAuth2 token revoked for {{self.client.provider}}")
            else:
                logger.warning(f"Failed to revoke OAuth2 token for {{self.client.provider}}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to revoke OAuth2 token: {{e}}")
            return False


# Global OAuth2 handler instance
oauth2_handler = OAuth2Handler()
'''
    
    def _generate_oauth2_models(self) -> str:
        """Generate OAuth2 models"""
        return '''"""
OAuth2 Models
Generated by ADOS Security Tools
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime


class OAuth2InitiateRequest(BaseModel):
    """OAuth2 initiate request model"""
    provider: str = Field(..., description="OAuth2 provider name")
    redirect_uri: Optional[HttpUrl] = Field(None, description="Custom redirect URI")


class OAuth2InitiateResponse(BaseModel):
    """OAuth2 initiate response model"""
    authorization_url: HttpUrl = Field(..., description="OAuth2 authorization URL")
    state: str = Field(..., description="CSRF state parameter")


class OAuth2CallbackRequest(BaseModel):
    """OAuth2 callback request model"""
    code: str = Field(..., description="Authorization code")
    state: str = Field(..., description="CSRF state parameter")


class OAuth2TokenResponse(BaseModel):
    """OAuth2 token response model"""
    access_token: str = Field(..., description="Access token")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    token_type: str = Field(..., description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    scope: str = Field(..., description="Token scope")


class OAuth2UserInfo(BaseModel):
    """OAuth2 user info model"""
    id: str = Field(..., description="User ID from provider")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User full name")
    picture: Optional[str] = Field(None, description="User profile picture URL")
    verified_email: bool = Field(default=False, description="Email verification status")
    locale: Optional[str] = Field(None, description="User locale")
    provider: str = Field(..., description="OAuth2 provider name")


class OAuth2RefreshRequest(BaseModel):
    """OAuth2 refresh token request model"""
    refresh_token: str = Field(..., description="Refresh token")


class OAuth2RevokeRequest(BaseModel):
    """OAuth2 revoke token request model"""
    token: str = Field(..., description="Token to revoke")
    token_type_hint: Optional[str] = Field(None, description="Token type hint")


class OAuth2ErrorResponse(BaseModel):
    """OAuth2 error response model"""
    error: str = Field(..., description="Error code")
    error_description: Optional[str] = Field(None, description="Error description")
    error_uri: Optional[HttpUrl] = Field(None, description="Error information URI")
    state: Optional[str] = Field(None, description="State parameter")
'''
    
    def _generate_oauth2_router(self, oauth2_spec: OAuth2Spec) -> str:
        """Generate OAuth2 router"""
        return f'''"""
OAuth2 Router
Generated by ADOS Security Tools
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from typing import Dict, Any
import logging

from .oauth2_models import *
from .oauth2_handlers import oauth2_handler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/oauth2", tags=["OAuth2"])


@router.post("/initiate", response_model=OAuth2InitiateResponse)
async def initiate_oauth2(request: OAuth2InitiateRequest) -> OAuth2InitiateResponse:
    """
    Initiate OAuth2 authentication flow
    """
    try:
        if request.provider != "{oauth2_spec.provider}":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {{request.provider}}"
            )
        
        result = oauth2_handler.initiate_oauth2_flow()
        
        return OAuth2InitiateResponse(
            authorization_url=result["authorization_url"],
            state=result["state"]
        )
        
    except Exception as e:
        logger.error(f"OAuth2 initiation failed: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not initiate OAuth2 flow"
        )


@router.get("/callback")
async def oauth2_callback(code: str, state: str) -> Dict[str, Any]:
    """
    Handle OAuth2 callback
    """
    try:
        result = await oauth2_handler.handle_oauth2_callback(code, state)
        
        # TODO: Create JWT tokens and redirect to frontend
        # This is a placeholder - integrate with your JWT system
        
        logger.info("OAuth2 callback processed successfully")
        
        return {{
            "message": "OAuth2 authentication successful",
            "user_info": result["user_info"]
        }}
        
    except Exception as e:
        logger.error(f"OAuth2 callback failed: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth2 callback failed"
        )


@router.post("/refresh", response_model=OAuth2TokenResponse)
async def refresh_oauth2_token(request: OAuth2RefreshRequest) -> OAuth2TokenResponse:
    """
    Refresh OAuth2 access token
    """
    try:
        tokens = await oauth2_handler.refresh_oauth2_token(request.refresh_token)
        
        return OAuth2TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            scope=tokens.get("scope", "")
        )
        
    except Exception as e:
        logger.error(f"OAuth2 token refresh failed: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh OAuth2 token"
        )


@router.post("/revoke")
async def revoke_oauth2_token(request: OAuth2RevokeRequest) -> Dict[str, str]:
    """
    Revoke OAuth2 token
    """
    try:
        result = await oauth2_handler.revoke_oauth2_token(request.token)
        
        if result:
            return {{"message": "Token revoked successfully"}}
        else:
            return {{"message": "Token revocation failed"}}
        
    except Exception as e:
        logger.error(f"OAuth2 token revocation failed: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not revoke OAuth2 token"
        )


@router.get("/providers")
async def get_oauth2_providers() -> Dict[str, Any]:
    """
    Get supported OAuth2 providers
    """
    return {{
        "providers": [
            {{
                "name": "{oauth2_spec.provider}",
                "scopes": {oauth2_spec.scope},
                "supported": True
            }}
        ]
    }}
'''
    
    def _scan_dependencies(self, vuln_spec: VulnerabilitySpec, output_path: Path) -> Dict[str, Any]:
        """Scan dependencies for vulnerabilities"""
        try:
            # Use safety for Python dependency scanning
            cmd = [sys.executable, "-m", "safety", "check", "--json"]
            
            if vuln_spec.include_dev_dependencies:
                cmd.append("--full-report")
            
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            vulnerabilities = []
            if result.stdout:
                try:
                    safety_results = json.loads(result.stdout)
                    for vuln in safety_results:
                        vulnerabilities.append({
                            "type": "dependency",
                            "package": vuln.get("package", ""),
                            "version": vuln.get("installed_version", ""),
                            "vulnerability_id": vuln.get("id", ""),
                            "severity": self._map_safety_severity(vuln.get("severity", "medium")),
                            "description": vuln.get("advisory", ""),
                            "fix": vuln.get("fix", "Update to latest version")
                        })
                except json.JSONDecodeError:
                    pass
            
            return {"vulnerabilities": vulnerabilities}
            
        except subprocess.TimeoutExpired:
            self.logger.error("Dependency scan timed out")
            return {"vulnerabilities": [], "error": "Scan timed out"}
        except Exception as e:
            self.logger.error(f"Dependency scan failed: {e}")
            return {"vulnerabilities": [], "error": str(e)}
    
    def _scan_code(self, vuln_spec: VulnerabilitySpec, output_path: Path) -> Dict[str, Any]:
        """Scan code for vulnerabilities"""
        try:
            vulnerabilities = []
            
            # Use bandit for Python code scanning
            cmd = [
                sys.executable, "-m", "bandit", 
                "-r", vuln_spec.target_path,
                "-f", "json",
                "-ll"  # Only show low severity and above
            ]
            
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.stdout:
                try:
                    bandit_results = json.loads(result.stdout)
                    for vuln in bandit_results.get("results", []):
                        vulnerabilities.append({
                            "type": "code",
                            "file": vuln.get("filename", ""),
                            "line": vuln.get("line_number", 0),
                            "test_id": vuln.get("test_id", ""),
                            "test_name": vuln.get("test_name", ""),
                            "severity": vuln.get("issue_severity", "medium").lower(),
                            "confidence": vuln.get("issue_confidence", "medium").lower(),
                            "description": vuln.get("issue_text", ""),
                            "code": vuln.get("code", "")
                        })
                except json.JSONDecodeError:
                    pass
            
            return {"vulnerabilities": vulnerabilities}
            
        except subprocess.TimeoutExpired:
            self.logger.error("Code scan timed out")
            return {"vulnerabilities": [], "error": "Scan timed out"}
        except Exception as e:
            self.logger.error(f"Code scan failed: {e}")
            return {"vulnerabilities": [], "error": str(e)}
    
    def _scan_owasp(self, vuln_spec: VulnerabilitySpec, output_path: Path) -> Dict[str, Any]:
        """Perform OWASP-based vulnerability assessment"""
        try:
            # This is a placeholder for OWASP scanning
            # In a real implementation, you might use tools like:
            # - OWASP ZAP
            # - semgrep with OWASP rules
            # - Custom OWASP Top 10 checks
            
            vulnerabilities = []
            
            # Simulate OWASP Top 10 checks
            owasp_checks = [
                ("A01:2021", "Broken Access Control", "Check for missing authorization"),
                ("A02:2021", "Cryptographic Failures", "Check for weak cryptography"),
                ("A03:2021", "Injection", "Check for SQL/NoSQL/Command injection"),
                ("A04:2021", "Insecure Design", "Check for insecure design patterns"),
                ("A05:2021", "Security Misconfiguration", "Check for security misconfigurations"),
                ("A06:2021", "Vulnerable Components", "Check for vulnerable dependencies"),
                ("A07:2021", "Authentication Failures", "Check for authentication weaknesses"),
                ("A08:2021", "Software Data Integrity", "Check for data integrity issues"),
                ("A09:2021", "Logging Failures", "Check for insufficient logging"),
                ("A10:2021", "SSRF", "Check for Server-Side Request Forgery")
            ]
            
            for owasp_id, category, description in owasp_checks:
                # Placeholder vulnerability (in real implementation, perform actual checks)
                vulnerabilities.append({
                    "type": "owasp",
                    "owasp_id": owasp_id,
                    "category": category,
                    "severity": "medium",
                    "description": description,
                    "status": "not_tested",
                    "recommendations": f"Implement {category} controls"
                })
            
            return {"vulnerabilities": vulnerabilities}
            
        except Exception as e:
            self.logger.error(f"OWASP scan failed: {e}")
            return {"vulnerabilities": [], "error": str(e)}
    
    def _analyze_threats(self, threat_spec: ThreatModelSpec) -> List[Dict[str, Any]]:
        """Analyze threats based on threat model specification"""
        threats = []
        
        # STRIDE threat categories
        stride_threats = {
            "Spoofing": "Identity spoofing attacks",
            "Tampering": "Data tampering attacks", 
            "Repudiation": "Non-repudiation attacks",
            "Information Disclosure": "Information disclosure attacks",
            "Denial of Service": "Denial of service attacks",
            "Elevation of Privilege": "Privilege escalation attacks"
        }
        
        for component in threat_spec.components:
            for threat_type, description in stride_threats.items():
                threats.append({
                    "id": f"{component}_{threat_type.lower().replace(' ', '_')}",
                    "component": component,
                    "threat_type": threat_type,
                    "description": f"{description} against {component}",
                    "severity": "medium",
                    "likelihood": "medium",
                    "impact": "medium"
                })
        
        return threats
    
    def _generate_mitigations(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate mitigation strategies for threats"""
        mitigations = []
        
        mitigation_strategies = {
            "spoofing": "Implement strong authentication mechanisms",
            "tampering": "Use data integrity checks and validation",
            "repudiation": "Implement comprehensive logging and audit trails",
            "information_disclosure": "Apply data encryption and access controls",
            "denial_of_service": "Implement rate limiting and input validation",
            "elevation_of_privilege": "Apply principle of least privilege"
        }
        
        for threat in threats:
            threat_type = threat["threat_type"].lower().replace(" ", "_")
            if threat_type in mitigation_strategies:
                mitigations.append({
                    "threat_id": threat["id"],
                    "strategy": mitigation_strategies[threat_type],
                    "implementation": f"Implement {mitigation_strategies[threat_type]} for {threat['component']}",
                    "priority": "high" if threat["severity"] == "high" else "medium"
                })
        
        return mitigations
    
    def _generate_vulnerability_report(self, scan_results: Dict[str, Any], vuln_spec: VulnerabilitySpec) -> Dict[str, Any]:
        """Generate vulnerability report"""
        vulnerabilities = scan_results.get("vulnerabilities", [])
        
        # Filter by severity threshold
        severity_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        threshold = severity_levels.get(vuln_spec.severity_threshold, 2)
        
        filtered_vulnerabilities = [
            v for v in vulnerabilities 
            if severity_levels.get(v.get("severity", "medium"), 2) >= threshold
        ]
        
        # Generate statistics
        stats = {
            "total_vulnerabilities": len(vulnerabilities),
            "filtered_vulnerabilities": len(filtered_vulnerabilities),
            "severity_breakdown": {}
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "medium")
            stats["severity_breakdown"][severity] = stats["severity_breakdown"].get(severity, 0) + 1
        
        return {
            "scan_type": vuln_spec.scan_type,
            "target_path": vuln_spec.target_path,
            "severity_threshold": vuln_spec.severity_threshold,
            "statistics": stats,
            "vulnerabilities": filtered_vulnerabilities,
            "generated_at": datetime.now().isoformat()
        }
    
    def _map_safety_severity(self, severity: str) -> str:
        """Map safety severity to standard levels"""
        severity_map = {
            "low": "low",
            "medium": "medium", 
            "high": "high",
            "critical": "critical"
        }
        return severity_map.get(severity.lower(), "medium")
    
    def get_tool_status(self) -> Dict[str, Any]:
        """Get status of security tools"""
        return {
            "tool_name": "SecurityTools",
            "version": "1.0.0",
            "capabilities": [
                "jwt_authentication",
                "oauth2_authentication",
                "vulnerability_scanning",
                "threat_modeling",
                "password_utilities"
            ],
            "project_root": str(self.project_root),
            "templates_directory": str(self.templates_dir),
            "status": "operational",
            "timestamp": datetime.now().isoformat()
        }