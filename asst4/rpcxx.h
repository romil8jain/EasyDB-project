// -*- c++ -*-
#ifndef RPCXX_H
#define RPCXX_H
 
#include <iostream>
#include <typeinfo>
#include <cstdlib>
#include "rpc.h"
 
namespace rpc {
  
// Protocol is used for encode and decode a type to/from the network.
//
// You may use network byte order, but it's optional. We won't test your code
// on two different architectures.
 
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

template <typename T1, typename T2> 
struct ProtocolUniversal {
  
   static constexpr size_t TYPE_SIZE1 = sizeof(T1);
   static constexpr size_t TYPE_SIZE2 = sizeof(T2);

   static bool Encode(uint8_t *out_bytes, uint32_t *out_len, const T1 &x, const T2 &y) {
       // check if buffer is big enough to fit the data, if not, return false
       if (*out_len < TYPE_SIZE1 + TYPE_SIZE2) return false;

       // do a memory copy of the data into the buffer, TYPE_SIZE is the size of the data
       memcpy(out_bytes, &x, TYPE_SIZE1);
       memcpy(out_bytes+TYPE_SIZE1, &y, TYPE_SIZE2);

       // since we wrote TYPE_SIZE number of bytes to the buffer, we set *out_len to TYPE_SIZE
       *out_len = TYPE_SIZE1 + TYPE_SIZE2;

       return true;
   }

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

// string, T
template<typename T> 
struct ProtocolUniversal<std::string, T> {
	static constexpr size_t TYPE_SIZE = sizeof(T);

	static bool Encode(uint8_t *out_bytes, uint32_t *out_len, const std::string &x, const T &y) {
		uint32_t orig_out_len = *out_len;
		bool encode_string = Protocol<std::string>::Encode(out_bytes, out_len, x);

		if (!encode_string) return false;

		uint32_t amount_written = *out_len;
		*out_len = orig_out_len-amount_written;
		bool encode_next = Protocol<T>::Encode(out_bytes+amount_written, out_len, y);

		if (!encode_next) return false;

		uint32_t amount_written2 = *out_len;
		*out_len = amount_written+amount_written2;

		return true;
	}

	static bool Decode(uint8_t *in_bytes, uint32_t *in_len, bool *ok, std::string &x, T &y) {
		// Check if the length of the buffer is big enough to read in num_bytes for string
		if (*in_len < 4) return false;

		uint32_t num_bytes = 0;
		memcpy(&num_bytes, in_bytes, 4);
	
		// check if buffer is big enough to read in x, if not, return false
		if (*in_len < (num_bytes+4+TYPE_SIZE)) return false;

		// Read in the string value
		std::string temp;	
		auto it_begin2 = in_bytes+4;
		auto it_end2 = in_bytes+4+num_bytes;
		
		for (auto i = it_begin2; i != it_end2; ++i)
		{
			temp += *i;
		}
		x = temp;

		memcpy(&y, in_bytes, TYPE_SIZE);

		// since we consumed num_bytes_4 number of bytes from the buffer, we set *in_len to num_bytes+4
		*in_len = num_bytes+4+TYPE_SIZE;
		return true;
	}
};

// T, string
template<typename T> 
struct ProtocolUniversal<T, std::string> {
	static constexpr size_t TYPE_SIZE = sizeof(T);

	static bool Encode(uint8_t *out_bytes, uint32_t *out_len, const T &y, const std::string &x) {
                uint32_t orig_out_len = *out_len;

		bool encode_T = Protocol<T>::Encode(out_bytes, out_len, y);

                if (!encode_T) return false;

                uint32_t amount_written = *out_len;
                *out_len = orig_out_len-amount_written;

		bool encode_string = Protocol<std::string>::Encode(out_bytes+amount_written, out_len, x);

                if (!encode_string) return false;

                uint32_t amount_written2 = *out_len;
                *out_len = amount_written+amount_written2;

                return true;
        }

	static bool Decode(uint8_t *in_bytes, uint32_t *in_len, bool *ok, T &y, std::string &x) {
		if (*in_len < TYPE_SIZE) return false;

		memcpy(&y, in_bytes, TYPE_SIZE);

		// Check if the length of the buffer is big enough to read in num_bytes for string
		if (*in_len < TYPE_SIZE+4) return false;

		uint32_t num_bytes = 0;
		memcpy(&num_bytes, in_bytes, 4);
	
		// check if buffer is big enough to read in x, if not, return false
		if (*in_len < (num_bytes+4+TYPE_SIZE)) return false;

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
		*in_len = num_bytes+4+TYPE_SIZE;
		return true;
	}
};

// string, string
template<> 
struct ProtocolUniversal<std::string, std::string> {
	static constexpr size_t TYPE_SIZE = sizeof(std::string);

	static bool Encode(uint8_t *out_bytes, uint32_t *out_len, const std::string &x, const std::string &y) {
                uint32_t orig_out_len = *out_len;

                bool encode_string1 = Protocol<std::string>::Encode(out_bytes, out_len, x);

                if (!encode_string1) return false;

                uint32_t amount_written = *out_len;
                *out_len = orig_out_len-amount_written;

                bool encode_string2 = Protocol<std::string>::Encode(out_bytes+amount_written, out_len, y);

                if (!encode_string2) return false;

                uint32_t amount_written2 = *out_len;
                *out_len = amount_written+amount_written2;

                return true;
        }

	static bool Decode(uint8_t *in_bytes, uint32_t *in_len, bool *ok, std::string &x, std::string &y) {
		// Check if the length of the buffer is big enough to read in num_bytes for x
		if (*in_len < 4) return false;

		uint32_t num_bytes_x = 0;
		memcpy(&num_bytes_x, in_bytes, 4);
	
		// check if buffer is big enough to read in x, if not, return false
			if (*in_len < (num_bytes_x+4)) return false;

		// Read in the string value
		std::string tempx;	
		auto it_begin = in_bytes+4;
		auto it_end = in_bytes+4+num_bytes_x;
		
		for (auto i = it_begin; i != it_end; ++i)
		{
			tempx += *i;
		}
		x = tempx;
		// End of getting first string x

		// Check if the length of the buffer is big enough to read in num_bytes for y
		if (*in_len < num_bytes_x+4+4) return false;

		uint32_t num_bytes_y = 0;
		memcpy(&num_bytes_y, in_bytes+num_bytes_x+4, 4);
	
		// check if buffer is big enough to read in y, if not, return false
		if (*in_len < (num_bytes_x+4+num_bytes_y+4)) return false;

		// Read in the string value
		std::string tempy;	
		auto it_begin2 = in_bytes+4+num_bytes_x+4;
		auto it_end2 = in_bytes+4+num_bytes_x+4+num_bytes_y;
		
		for (auto i = it_begin2; i != it_end2; ++i)
		{
			tempy += *i;
		}
		y = tempy;
		// end of second string y
	
		// since we consumed num_bytes_4 number of bytes from the buffer, we set *in_len to num_bytes+4
		*in_len = num_bytes_x+4+num_bytes_y+4;
		return true;
	}
};
 
// TASK2: Client-side
/*class IntParam : public BaseParams {
   int p;
   public:
   IntParam(int p) : p(p) {}
 
   bool Encode(uint8_t *out_bytes, uint32_t *out_len) const override {
   return Protocol<int>::Encode(out_bytes, out_len, p);
   }
};*/

// Two arguments case
template <typename T1, typename T2>
class TwoParam : public BaseParams {
   T1 p1;
   T2 p2;

   public:
   TwoParam(T1 p1, T2 p2) : p1(p1), p2(p2) {}

   bool Encode(uint8_t *out_bytes, uint32_t *out_len) const override {
        return ProtocolUniversal<T1, T2>::Encode(out_bytes, out_len, p1, p2);
   }
};

// One argument
template <typename T>
class Param : public BaseParams {
   T p;
   public:
   Param(T p) : p(p) {}
 
   bool Encode(uint8_t *out_bytes, uint32_t *out_len) const override {
		return Protocol<T>::Encode(out_bytes, out_len, p);
   }
};

// no arguments case
class NoParam : public BaseParams {
   public:
   NoParam() {}
 
   bool Encode(uint8_t *out_bytes, uint32_t *out_len) const override {
	*out_len = 0;
	return true; // not sure if should be true or false
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
   int result = (((Svc *) instance)->*p)(x);
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
 
// TASK2: Client-side
/*class IntResult : public BaseResult {
   int r;
 
   public:
   bool HandleResponse(uint8_t *in_bytes, uint32_t *in_len, bool *ok) override final {
   return Protocol<int>::Decode(in_bytes, in_len, ok, r);
   }
   int &data() { return r; }
};*/

template <typename T>
class Result : public BaseResult{
	T r;

public:
	T &data() { return r; }
	bool HandleResponse(uint8_t *in_bytes, uint32_t *in_len, bool *ok) override final
	{
		return Protocol<T>::Decode(in_bytes, in_len, ok, r);
	}
};

template <>
class Result<void> : public BaseResult {
public:
	bool HandleResponse(uint8_t *in_bytes, uint32_t *in_len, bool *ok) override final
	{
		*in_len = 0;
		return true; // not sure about this
	}
}; 

// TASK2: Client-side
class Client : public BaseClient {
public:
/*   template <typename Svc>
   Result<int> *Call(Svc *svc, int (Svc::*func)(int), int x) {
   // Lookup instance and function IDs.
   int instance_id = svc->instance_id();
   int func_id = svc->LookupExportFunction(MemberFunctionPtr::From(func));
 
   // This incomplete solution only works for this type of member functions.
   // So the result must be an integer.
   auto result = new Result<int>();
 
   // We also send the paramters of the functions. For this incomplete
   // solution, it must be one integer.
   if (!Send(instance_id, func_id, new IntParam(x), result)) {
       // Fail to send, then delete the result and return nullptr.
       delete result;
       return nullptr;
   }
   return result;
   }
*/
    template <typename Svc, typename RT, typename T>
    Result<RT> *Call(Svc *svc, RT (Svc::*func)(T), T x) {
	// Lookup instance and function IDs.
	int instance_id = svc->instance_id();
	int func_id = svc->LookupExportFunction(MemberFunctionPtr::From(func));
		
	// This incomplete solution only works for this type of member functions.
	// So the result must be an integer.
	auto result = new Result<RT>();
	
	// We also send the paramters of the functions. For this incomplete
	// solution, it must be one integer.
	if (!Send(instance_id, func_id, new Param<T>(x), result)) {
		// Fail to send, then delete the result and return nullptr.
		delete result;
		return nullptr;
	}
	return result;
   }
 
   // no arguments case
   template <typename Svc, typename RT>
    Result<RT> *Call(Svc *svc, RT (Svc::*func)()) {
        // Lookup instance and function IDs.
        int instance_id = svc->instance_id();
        int func_id = svc->LookupExportFunction(MemberFunctionPtr::From(func));

        // This incomplete solution only works for this type of member functions.
        // So the result must be an integer.
        auto result = new Result<RT>();

        // We also send the paramters of the functions. 
	// Not sure what to send as params for the case where there are no params
        if (!Send(instance_id, func_id, new NoParam(), result)) {
                // Fail to send, then delete the result and return nullptr.
                delete result;
                return nullptr;
        }
        return result;
   }

    // Two arguments case
    template <typename Svc, typename RT, typename T1, typename T2>
    Result<RT> *Call(Svc *svc, RT (Svc::*func)(T1, T2), T1 x, T2 y) {
        // Lookup instance and function IDs.
        int instance_id = svc->instance_id();
        int func_id = svc->LookupExportFunction(MemberFunctionPtr::From(func));

        // This incomplete solution only works for this type of member functions.
        // So the result must be an integer.
        auto result = new Result<RT>();

        // We also send the paramters of the functions. For this incomplete
        // solution, it must be one integer.
        if (!Send(instance_id, func_id, new TwoParam<T1, T2>(x, y), result)) {
                // Fail to send, then delete the result and return nullptr.
                delete result;
                return nullptr;
        }
        return result;
   }
};
 
// TASK2: Server-side
template <typename Svc>
class Service : public BaseService {
protected:
   void Export(int (Svc::*func)(int)) {
   ExportRaw(MemberFunctionPtr::From(func), new IntIntProcedure<Svc>());
   }
   /* add this */
   template<typename MemberFunction>
   void Export(MemberFunction f) {
     std::cout << "WARNING: Exporting "
               << typeid(MemberFunction).name()
               << " is not supported\n";
   }
   /* end here */
};
 
}
 
#endif /* RPCXX_H */
 


