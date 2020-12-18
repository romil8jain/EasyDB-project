// -*- c++ -*-
#ifndef RPCXX_H
#define RPCXX_H
 
#include <iostream>
#include <typeinfo>
#include <cstdlib>
#include "rpc.h"
 
namespace rpc {
  
// Protocol is used for encode and decode a type to/from the network.
 
// TASK1: add more specializations to Protocol template class to support more
// types.
template <typename T> struct Protocol {
  
   static constexpr size_t TYPE_SIZE = sizeof(T);
   /* out_bytes: Write data into this buffer. It's size is equal to *out_len
    *   out_len: Initially, *out_len tells you the size of the buffer out_bytes.
    *            However, it is also used as a return value, so you must set *out_len
    *            to the number of bytes you wrote to the buffer.
    *         x: the data you want to write to buffer
    */    
   static bool Encode(uint8_t *out_bytes, uint32_t *out_len, const T &x) {
   // check if buffer is big enough to fit the data, if not, return false
       if (*out_len < TYPE_SIZE) return false;
 
       // do a memory copy of the data into the buffer, TYPE_SIZE is the size of the data
       memcpy(out_bytes, &x, TYPE_SIZE);
 
       // since we wrote TYPE_SIZE number of bytes to the buffer, we set *out_len to TYPE_SIZE
       *out_len = TYPE_SIZE;
 
       return true;
   }
  
   /* in_bytes: Read data from this buffer. It's size is equal to *in_len
    *   in_len: Initially, *in_len tells you the size of the buffer in_bytes.
    *           However, it is also used as a return value, so you must set *in_len
    *           to the number of bytes you consume from the buffer.
    *        x: the data you want to read from the buffer
    */  
   static bool Decode(uint8_t *in_bytes, uint32_t *in_len, bool *ok, T &x) {
   // check if buffer is big enough to read in x, if not, return false
       if (*in_len < TYPE_SIZE) return false;
 
       // do a memory copy from the buffer into the data, TYPE_SIZE is the size of the data
       memcpy(&x, in_bytes, TYPE_SIZE);
 
       // since we consumed TYPE_SIZE number of bytes from the buffer, we set *in_len to TYPE_SIZE
       *in_len = TYPE_SIZE;
 
       return true;
   }
};
 
template <typename T1, typename T2> struct ProtocolUniversal {
  
   static constexpr size_t TYPE_SIZE1 = sizeof(T1);
   static constexpr size_t TYPE_SIZE2 = sizeof(T2);


   static bool Decode(uint8_t *in_bytes, uint32_t *in_len, bool *ok, T1 &x, T2 &y) {
   // check if buffer is big enough to read in x, if not, return false
       if (*in_len < (TYPE_SIZE1 + TYPE_SIZE2)) return false;
 
       // do a memory copy from the buffer into the data, TYPE_SIZE is the size of the data
       memcpy(&x, in_bytes, TYPE_SIZE1);
	   memcpy(&y, in_bytes + TYPE_SIZE1, TYPE_SIZE2)
 
       // since we consumed TYPE_SIZE number of bytes from the buffer, we set *in_len to TYPE_SIZE
       *in_len = TYPE_SIZE1 + TYPE_SIZE2;
 
       return true;
   }
};
 
template <>
struct Protocol<std::string> {
    static constexpr size_t TYPE_SIZE = sizeof(std::string);
 
    static bool Encode(uint8_t *out_bytes, uint32_t *out_len, const std::string &x) {
    	uint32_t num_bytes = x.length();

    	// check if buffer is big enough to fit the data, if not, return false
    	if (*out_len < (num_bytes+4)) return false;

    	// Copy the size of the string into the biffer
    	memcpy(out_bytes, &num_bytes, sizeof(uint32_t));
	// Copy the actual string into the buffer
	memcpy(out_bytes+4, (x.data()), num_bytes);
  
    	*out_len = num_bytes+4;
       	return true;
   }
 
   static bool Decode(uint8_t *in_bytes, uint32_t *in_len, bool *ok, std::string &x) {
	// Check if the length of the buffer is big enough to read in num_bytes
	if (*in_len < 4) return false;

	uint32_t num_bytes = 0;
   	memcpy(&num_bytes, in_bytes, 4);
  
 	// check if buffer is big enough to read in x, if not, return false
       	if (*in_len < (num_bytes+4)) return false;

	// Read in the string value
	std::string temp;	
	auto it_begin2 = in_bytes+4;
	auto it_end2 = in_bytes+4+num_bytes;
	
	for (auto i = it_begin2; i != it_end2; ++i)
	{
	    temp += *i;
	}
	x = temp;
 
       	// since we consumed num_bytes_4 number of bytes from the buffer, we set *in_len to num_bytes+4
       	*in_len = num_bytes+4;
       	return true;
   }
};
 
// TASK2: Client-side
class IntParam : public BaseParams {
   int p;
   public:
   IntParam(int p) : p(p) {}
 
   bool Encode(uint8_t *out_bytes, uint32_t *out_len) const override {
   return Protocol<int>::Encode(out_bytes, out_len, p);
   }
};
 
// TASK2: Server-side
template <typename Svc>
class IntIntProcedure : public BaseProcedure {
   bool DecodeAndExecute(uint8_t *in_bytes, uint32_t *in_len,
                       uint8_t *out_bytes, uint32_t *out_len,
                       bool *ok) override final { 

		int x;
		// This function is similar to Decode. We need to return false if buffer
		// isn't large enough, or fatal error happens during parsing.
		if (!Protocol<int>::Decode(in_bytes, in_len, ok, x) || !*ok) {
			return false;
		}
		// Now we cast the function pointer func_ptr to its original type.
		//
		// This incomplete solution only works for this type of member functions.
		using FunctionPointerType = int (Svc::*)(int);
		auto p = func_ptr.To<FunctionPointerType>();

		// EXECUTION STEP: we call the function of the Svc class here and get the result and encode the result
		int result = (((Svc *) instance)->*p)(x); // The svc class here inherits from the service class so typecasting is allowed

		if (!Protocol<int>::Encode(out_bytes, out_len, result)) {
			// out_len should always be large enough so this branch shouldn't be
			// taken. However just in case, we return an fatal error by setting *ok
			// to false.
			*ok = false;
			return false;
		}
		return true;
   }
};


// TASK2: Server-side SPECIALIZATION

// void with return void implementation
template <typename Svc>
class UniversalProcedure : public BaseProcedure {
   bool DecodeAndExecute(uint8_t *in_bytes, uint32_t *in_len,
                       uint8_t *out_bytes, uint32_t *out_len,
                       bool *ok) override final { 


		*in_len = 0;
		// Now we cast the function pointer func_ptr to its original type.
		//
		// This incomplete solution only works for this type of member functions.
		using FunctionPointerType = void (Svc::*)();
		auto p = func_ptr.To<FunctionPointerType>();

		// EXECUTION STEP: we call the function of the Svc class here and get the result and encode the result
		(((Svc *) instance)->*p)(); // The svc class here inherits from the service class so typecasting is allowed

		return true;
   }
};

//void with 2 parameters
template <typename Svc, void, typename T1, typename T2>
class UniversalProcedure : public BaseProcedure {
   bool DecodeAndExecute(uint8_t *in_bytes, uint32_t *in_len,
                       uint8_t *out_bytes, uint32_t *out_len,
                       bool *ok) override final { 


		T1 x;
		T2 y;
		// This function is similar to Decode. We need to return false if buffer
		// isn't large enough, or fatal error happens during parsing.
		if (!ProtocolUniversal<T1, T2>::Decode(in_bytes, in_len, ok, x, y) || !*ok) {
			return false;
		}

		// Now we cast the function pointer func_ptr to its original type.
		//
		// This incomplete solution only works for this type of member functions.
		using FunctionPointerType = void (Svc::*)(T1, T2);
		auto p = func_ptr.To<FunctionPointerType>();

		// EXECUTION STEP: we call the function of the Svc class here and get the result and encode the result
		(((Svc *) instance)->*p)(x, y); // The svc class here inherits from the service class so typecasting is allowed

		return true;
   }
};

//void with 1 strings
template <typename Svc, void, std::string, typename T2>
class UniversalProcedure : public BaseProcedure {
   bool DecodeAndExecute(uint8_t *in_bytes, uint32_t *in_len,
                       uint8_t *out_bytes, uint32_t *out_len,
                       bool *ok) override final { 


		std::string x;
		T2 y;
		// This function is similar to Decode. We need to return false if buffer
		// isn't large enough, or fatal error happens during parsing.
		if (!ProtocolUniversal<std::string, T2>::Decode(in_bytes, in_len, ok, x, y) || !*ok) {
			return false;
		}

		// Now we cast the function pointer func_ptr to its original type.
		//
		// This incomplete solution only works for this type of member functions.
		using FunctionPointerType = void (Svc::*)(std::string, T2);
		auto p = func_ptr.To<FunctionPointerType>();

		// EXECUTION STEP: we call the function of the Svc class here and get the result and encode the result
		(((Svc *) instance)->*p)(x, y); // The svc class here inherits from the service class so typecasting is allowed

		return true;
   }
};

// 1 params and a return type: non string
template <typename Svc, typename RT, typename T1>
class UniversalProcedure : public BaseProcedure {
   bool DecodeAndExecute(uint8_t *in_bytes, uint32_t *in_len,
                       uint8_t *out_bytes, uint32_t *out_len,
                       bool *ok) override final { 


		T1 x;
		// This function is similar to Decode. We need to return false if buffer
		// isn't large enough, or fatal error happens during parsing.
		if (!ProtocolUniversal<T1>::Decode(in_bytes, in_len, ok, x) || !*ok) {
			return false;
		}

		// Now we cast the function pointer func_ptr to its original type.
		//
		// This incomplete solution only works for this type of member functions.
		using FunctionPointerType = RT (Svc::*)(T1);
		auto p = func_ptr.To<FunctionPointerType>();

		// EXECUTION STEP: we call the function of the Svc class here and get the result and encode the result
		RT result = (((Svc *) instance)->*p)(x); // The svc class here inherits from the service class so typecasting is allowed

		if (!Protocol<RT>::Encode(out_bytes, out_len, result)) {
			// out_len should always be large enough so this branch shouldn't be
			// taken. However just in case, we return an fatal error by setting *ok
			// to false.
			*ok = false;
			return false;
		}
		return true;
   }
};


// 2 params and a return type: non string
template <typename Svc, typename RT, typename T1, typename T2>
class UniversalProcedure : public BaseProcedure {
   bool DecodeAndExecute(uint8_t *in_bytes, uint32_t *in_len,
                       uint8_t *out_bytes, uint32_t *out_len,
                       bool *ok) override final { 


		T1 x;
		T2 y;
		// This function is similar to Decode. We need to return false if buffer
		// isn't large enough, or fatal error happens during parsing.
		if (!ProtocolUniversal<T1, T2>::Decode(in_bytes, in_len, ok, x, y) || !*ok) {
			return false;
		}

		// Now we cast the function pointer func_ptr to its original type.
		//
		// This incomplete solution only works for this type of member functions.
		using FunctionPointerType = RT (Svc::*)(T1, T2);
		auto p = func_ptr.To<FunctionPointerType>();

		// EXECUTION STEP: we call the function of the Svc class here and get the result and encode the result
		RT result = (((Svc *) instance)->*p)(x, y); // The svc class here inherits from the service class so typecasting is allowed

		if (!Protocol<RT>::Encode(out_bytes, out_len, result)) {
			// out_len should always be large enough so this branch shouldn't be
			// taken. However just in case, we return an fatal error by setting *ok
			// to false.
			*ok = false;
			return false;
		}
		return true;
   }
};

// 2 params and a return type: first string
template <typename Svc, typename RT, std::string, typename T2>
class UniversalProcedure : public BaseProcedure {
   bool DecodeAndExecute(uint8_t *in_bytes, uint32_t *in_len,
                       uint8_t *out_bytes, uint32_t *out_len,
                       bool *ok) override final { 

		std::string x;				   
		T2 y;
		// This function is similar to Decode. We need to return false if buffer
		// isn't large enough, or fatal error happens during parsing.
		if (!ProtocolUniversal<std::string, T2>::Decode(in_bytes, in_len, ok, x, y) || !*ok) {
			return false;
		}

		// Now we cast the function pointer func_ptr to its original type.
		//
		// This incomplete solution only works for this type of member functions.
		using FunctionPointerType = RT (Svc::*)(std::string, T2);
		auto p = func_ptr.To<FunctionPointerType>();

		// EXECUTION STEP: we call the function of the Svc class here and get the result and encode the result
		RT result = (((Svc *) instance)->*p)(x, y); // The svc class here inherits from the service class so typecasting is allowed

		if (!Protocol<RT>::Encode(out_bytes, out_len, result)) {
			// out_len should always be large enough so this branch shouldn't be
			// taken. However just in case, we return an fatal error by setting *ok
			// to false.
			*ok = false;
			return false;
		}
		return true;
   }
};

// 2 params and a return type: second string
template <typename Svc, typename RT, typename T2, std::string>
class UniversalProcedure : public BaseProcedure {
   bool DecodeAndExecute(uint8_t *in_bytes, uint32_t *in_len,
                       uint8_t *out_bytes, uint32_t *out_len,
                       bool *ok) override final { 
			   
		T1 x;
		std::string y;
		// This function is similar to Decode. We need to return false if buffer
		// isn't large enough, or fatal error happens during parsing.
		if (!ProtocolUniversal<T1, std::string>::Decode(in_bytes, in_len, ok, x, y) || !*ok) {
			return false;
		}

		// Now we cast the function pointer func_ptr to its original type.
		//
		// This incomplete solution only works for this type of member functions.
		using FunctionPointerType = RT (Svc::*)(T1, std::string);
		auto p = func_ptr.To<FunctionPointerType>();

		// EXECUTION STEP: we call the function of the Svc class here and get the result and encode the result
		RT result = (((Svc *) instance)->*p)(x, y); // The svc class here inherits from the service class so typecasting is allowed

		if (!Protocol<RT>::Encode(out_bytes, out_len, result)) {
			// out_len should always be large enough so this branch shouldn't be
			// taken. However just in case, we return an fatal error by setting *ok
			// to false.
			*ok = false;
			return false;
		}
		return true;
   }
};

// 2 params and a return type: second string
template <typename Svc, typename RT, std::string, std::string>
class UniversalProcedure : public BaseProcedure {
   bool DecodeAndExecute(uint8_t *in_bytes, uint32_t *in_len,
                       uint8_t *out_bytes, uint32_t *out_len,
                       bool *ok) override final { 
			   
		std::string x;
		std::string y;
		// This function is similar to Decode. We need to return false if buffer
		// isn't large enough, or fatal error happens during parsing.
		if (!ProtocolUniversal<std::string, std::string>::Decode(in_bytes, in_len, ok, x, y) || !*ok) {
			return false;
		}

		// Now we cast the function pointer func_ptr to its original type.
		//
		// This incomplete solution only works for this type of member functions.
		using FunctionPointerType = RT (Svc::*)(std::string, std::string);
		auto p = func_ptr.To<FunctionPointerType>();

		// EXECUTION STEP: we call the function of the Svc class here and get the result and encode the result
		RT result = (((Svc *) instance)->*p)(x, y); // The svc class here inherits from the service class so typecasting is allowed

		if (!Protocol<RT>::Encode(out_bytes, out_len, result)) {
			// out_len should always be large enough so this branch shouldn't be
			// taken. However just in case, we return an fatal error by setting *ok
			// to false.
			*ok = false;
			return false;
		}
		return true;
   }
};


// TASK2: Client-side
class IntResult : public BaseResult {
   int r;
 
   public:
   bool HandleResponse(uint8_t *in_bytes, uint32_t *in_len, bool *ok) override final {
   return Protocol<int>::Decode(in_bytes, in_len, ok, r);
   }
   int &data() { return r; }
};
 
template<typename T>
class Result {
 T r;
public:
 T &data() { return r; }
};
 
template<>
class Result<void> {};
 
// TASK2: Client-side
class Client : public BaseClient {
public:
   template <typename Svc>
   IntResult *Call(Svc *svc, int (Svc::*func)(int), int x) {
   // Lookup instance and function IDs.
   int instance_id = svc->instance_id();
   int func_id = svc->LookupExportFunction(MemberFunctionPtr::From(func));
 
   // This incomplete solution only works for this type of member functions.
   // So the result must be an integer.
   auto result = new IntResult();
 
   // We also send the paramters of the functions. For this incomplete
   // solution, it must be one integer.
   if (!Send(instance_id, func_id, new IntParam(x), result)) {
       // Fail to send, then delete the result and return nullptr.
       delete result;
       return nullptr;
   }
   return result;
   }
 
   /* add this */
   template<typename Svc, typename RT, typename ... FA>
   Result<RT> * Call(Svc *svc, RT (Svc::*f)(FA...), ...) {
     std::cout << "WARNING: Calling "
           << typeid(decltype(f)).name()
           << " is not supported\n";
     return nullptr;
   }
   /* end here */
};
 
// TASK2: Server-side
template <typename Svc>
class Service : public BaseService {
protected:
   void Export(int (Svc::*func)(int)) {
		ExportRaw(MemberFunctionPtr::From(func), new IntIntProcedure<Svc>());
   }

   template<typename RT, typename T1>
   void Export(RT (Svc::*func)(T1)){
	   ExportRaw(MemberFunctionPtr::From(func), new UniversalProcedure<Svc, RT, T1>());
   }

   template<typename RT, typename T1, typename T2>
   void Export(RT (Svc::*func)(T1, T2)){
	   ExportRaw(MemberFunctionPtr::From(func), new UniversalProcedure<Svc, RT, T1, T2>());
   }

   template<void, typename T1>
   void Export(void (Svc::*func)(T1)){
	   ExportRaw(MemberFunctionPtr::From(func), new UniversalProcedure<Svc, void, T1>());
   }

   template<void, typename T1, typename T2>
   void Export(void (Svc::*func)(T1, T2)){
	   ExportRaw(MemberFunctionPtr::From(func), new UniversalProcedure<Svc, void, T1, T2>());
   }
   
   /* add this */
   template<typename RT, typename ... Args>
   void Export(RT (Svc::*func)(Args ...)) {
	//    ExportRaw(MemberFunctionPtr::From(func), new UniversalProcedure<Svc, RT, Args ...>());
	cout << "unimplemented"
   }
   /* end here */
};
 
}
 
#endif /* RPCXX_H */
 




// Deleted server side code


// // TASK2: Server-side: Trying to make universal procedure (probably not for strings)
// template <typename Svc, typename RT, typename ... Args>
// class UniversalProcedure : public BaseProcedure {

// 	template<typename T, typename ... Vargs, typename ... FinalArgs> 
// 	bool DecodeRecursive(uint8_t *in_bytes, uint32_t *in_len,
//                        uint8_t *out_bytes, uint32_t *out_len,
//                        bool *ok,  FinalArgs ... finalargs)  {  // passing by reference here?
//                         //override means don’t allow derived class to override the base class’ virtual function
// 		T x;
// 		// This function is similar to Decode. We need to return false if buffer
// 		// isn't large enough, or fatal error happens during parsing.
// 		if (!ProtocolUniversal<T>::Decode(in_bytes, in_len, ok, x) || !*ok) {
// 			return false;
// 		}
// 		return DecodeRecursive<Vargs ...>(uint8_t *in_bytes, uint32_t *in_len,
//                        uint8_t *out_bytes, uint32_t *out_len,
//                        bool *ok, finalargs ..., x);
//    }

// 	template<> 
//     bool DecodeRecursive(uint8_t *in_bytes, uint32_t *in_len,
//                        uint8_t *out_bytes, uint32_t *out_len,
//                        bool *ok, ... &finalargs)  { 

// 		using FunctionPointerType = RT (Svc::*)(finalargs ...);
// 		auto p = func_ptr.To<FunctionPointerType>();

// 		// EXECUTION STEP: we call the function of the Svc class here and get the result and encode the result
// 		RT result = (((Svc *) instance)->*p)(x); // The svc class here inherits from the service class so typecasting is allowed
		
// 		if (!Protocol<RT>::Encode(out_bytes, out_len, result)) {
// 			// out_len should always be large enough so this branch shouldn't be
// 			// taken. However just in case, we return an fatal error by setting *ok
// 			// to false.
// 			*ok = false;
// 			return false;
// 		}
// 		return true;
//    }
   		
//    bool DecodeAndExecute(uint8_t *in_bytes, uint32_t *in_len,
//                        uint8_t *out_bytes, uint32_t *out_len,
//                        bool *ok) override final { 

// 		return DecodeRecursive<Args ...>(uint8_t *in_bytes, uint32_t *in_len,
//                        uint8_t *out_bytes, uint32_t *out_len,
//                        bool *ok);

		
//    }
// };
