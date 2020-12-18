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
	int num_bytes = x.length();
//	std::cout << "sizeof(num_bytes): " << sizeof(int) << std::endl;
	// check if buffer is big enough to fit the data, if not, return false
        if (*out_len < (num_bytes+4)) return false;

	// Copy the size of the string into the biffer
	memcpy(out_bytes, &(num_bytes), sizeof(int));
	
	// Create a temporary string
	char* temp;
	memcpy(&temp, &x, num_bytes);
	memcpy(out_bytes+4, temp, num_bytes);
	
        *out_len = num_bytes+4;
	std::cout << "out len: " << *out_len << std::endl;
        return true;
    }

    static bool Decode(uint8_t *in_bytes, uint32_t *in_len, bool *ok, std::string &x) {
	int num_bytes = 0;
	std::cout << "Inside decode" << std::endl;
	memcpy(&num_bytes, in_bytes, 4); //get string length
	// check if buffer is big enough to read in x, if not, return false

	std::cout << "DECODE: in_len: " << *in_len << ", num_bytes: " << num_bytes << std::endl;

        if (*in_len < (num_bytes+4)) return false;

        // do a memory copy from the buffer into the data, TYPE_SIZE is the size of the data
	char* temp;
	memcpy(&temp, in_bytes+4, num_bytes);
	memcpy(&x, temp, num_bytes);
	std::cout << "DECODE: string is " << x << std::endl;

        // since we consumed TYPE_SIZE number of bytes from the buffer, we set *in_len to TYPE_SIZE
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